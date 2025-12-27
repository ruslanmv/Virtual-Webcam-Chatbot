"""
System audio loopback capture (Windows WASAPI)

Captures system audio output for meeting audio monitoring.

Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

import queue
import sys
from typing import Callable, Optional

import numpy as np
import sounddevice as sd


class LoopbackCapture:
    """
    System audio loopback capture.

    Captures audio from system output (what you hear) using WASAPI loopback
    on Windows. This allows monitoring meeting audio from Zoom, Teams, etc.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 480,
        device: Optional[int] = None,
    ):
        """
        Initialize loopback capture

        Args:
            sample_rate: Sample rate in Hz
            channels: Number of channels (1 = mono)
            chunk_size: Audio chunk size in frames
            device: Loopback device index (None = auto-detect)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size

        # Auto-detect loopback device if not specified
        if device is None:
            device = self._find_loopback_device()

        self.device = device

        self._stream: Optional[sd.InputStream] = None
        self._is_running = False
        self._callback: Optional[Callable[[bytes], None]] = None
        self._queue: Optional[queue.Queue] = None

    def _find_loopback_device(self) -> Optional[int]:
        """
        Find the default loopback device on Windows

        Returns:
            Device index or None if not found
        """
        if sys.platform != "win32":
            print("Warning: Loopback capture is primarily for Windows WASAPI")
            return None

        devices = sd.query_devices()

        # Look for devices with "Stereo Mix", "What U Hear", or loopback in name
        loopback_keywords = ["stereo mix", "what u hear", "loopback", "wave out mix"]

        for idx, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                device_name = device["name"].lower()
                if any(keyword in device_name for keyword in loopback_keywords):
                    return idx

        # On Windows, try to use WASAPI loopback via hostapi
        for idx, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                hostapi = sd.query_hostapis(device["hostapi"])
                if "wasapi" in hostapi["name"].lower():
                    # This might be a loopback device
                    return idx

        print("Warning: No loopback device found. You may need to enable Stereo Mix.")
        return None

    def start(
        self,
        callback: Optional[Callable[[bytes], None]] = None,
        use_queue: bool = False,
    ) -> Optional[queue.Queue]:
        """
        Start capturing system audio

        Args:
            callback: Optional callback function for audio data
            use_queue: If True, return a queue for audio data

        Returns:
            Queue object if use_queue=True, else None
        """
        if self._is_running:
            raise RuntimeError("Capture already running")

        if self.device is None:
            raise RuntimeError(
                "No loopback device available. "
                "On Windows, enable 'Stereo Mix' in recording devices."
            )

        self._callback = callback
        self._is_running = True

        if use_queue:
            self._queue = queue.Queue(maxsize=100)

        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Loopback capture status: {status}")

            # Convert to mono if stereo
            if indata.shape[1] > 1:
                audio = np.mean(indata, axis=1, keepdims=True)
            else:
                audio = indata

            # Convert float32 to int16 PCM
            pcm16 = (audio[:, 0] * 32767).astype(np.int16).tobytes()

            # Deliver via callback
            if self._callback:
                try:
                    self._callback(pcm16)
                except Exception as e:
                    print(f"Error in loopback callback: {e}")

            # Deliver via queue
            if self._queue:
                try:
                    self._queue.put_nowait(pcm16)
                except queue.Full:
                    pass

        try:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=2,  # Loopback is often stereo
                dtype="float32",
                callback=audio_callback,
                blocksize=self.chunk_size,
                device=self.device,
            )

            self._stream.start()
        except Exception as e:
            print(f"Error starting loopback capture: {e}")
            self._is_running = False
            raise

        return self._queue

    def stop(self) -> None:
        """Stop capturing audio"""
        if not self._is_running:
            return

        self._is_running = False

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        self._callback = None
        self._queue = None

    def is_running(self) -> bool:
        """Check if capture is running"""
        return self._is_running

    @staticmethod
    def list_loopback_devices() -> list[dict]:
        """
        List available loopback devices

        Returns:
            List of potential loopback device info
        """
        devices = sd.query_devices()
        loopback_devices = []

        loopback_keywords = ["stereo mix", "what u hear", "loopback", "wave out mix"]

        for idx, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                device_name = device["name"].lower()
                if any(keyword in device_name for keyword in loopback_keywords):
                    loopback_devices.append(
                        {
                            "index": idx,
                            "name": device["name"],
                            "channels": device["max_input_channels"],
                            "sample_rate": device["default_samplerate"],
                        }
                    )

        return loopback_devices

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
