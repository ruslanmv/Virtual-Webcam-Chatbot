"""
Microphone audio capture

Captures audio from the default microphone input.

Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

import queue
import threading
from typing import Callable, Optional

import numpy as np
import sounddevice as sd


class MicrophoneCapture:
    """
    Microphone audio capture using sounddevice.

    Captures audio from the default microphone and delivers
    PCM16 audio data via callback or queue.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 480,  # 30ms at 16kHz
        device: Optional[int] = None,
    ):
        """
        Initialize microphone capture

        Args:
            sample_rate: Sample rate in Hz
            channels: Number of channels (1 = mono, 2 = stereo)
            chunk_size: Audio chunk size in frames
            device: Device index (None = default)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.device = device

        self._stream: Optional[sd.InputStream] = None
        self._is_running = False
        self._callback: Optional[Callable[[bytes], None]] = None
        self._queue: Optional[queue.Queue] = None

    def start(
        self,
        callback: Optional[Callable[[bytes], None]] = None,
        use_queue: bool = False,
    ) -> Optional[queue.Queue]:
        """
        Start capturing audio

        Args:
            callback: Optional callback function for audio data
            use_queue: If True, return a queue for audio data

        Returns:
            Queue object if use_queue=True, else None
        """
        if self._is_running:
            raise RuntimeError("Capture already running")

        self._callback = callback
        self._is_running = True

        if use_queue:
            self._queue = queue.Queue(maxsize=100)

        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Mic capture status: {status}")

            # Convert float32 to int16 PCM
            pcm16 = (indata[:, 0] * 32767).astype(np.int16).tobytes()

            # Deliver via callback
            if self._callback:
                try:
                    self._callback(pcm16)
                except Exception as e:
                    print(f"Error in mic callback: {e}")

            # Deliver via queue
            if self._queue:
                try:
                    self._queue.put_nowait(pcm16)
                except queue.Full:
                    pass  # Drop frame if queue is full

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=audio_callback,
            blocksize=self.chunk_size,
            device=self.device,
        )

        self._stream.start()
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
    def list_devices() -> list[dict]:
        """
        List available audio input devices

        Returns:
            List of device info dictionaries
        """
        devices = sd.query_devices()
        input_devices = []

        for idx, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                input_devices.append(
                    {
                        "index": idx,
                        "name": device["name"],
                        "channels": device["max_input_channels"],
                        "sample_rate": device["default_samplerate"],
                    }
                )

        return input_devices

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
