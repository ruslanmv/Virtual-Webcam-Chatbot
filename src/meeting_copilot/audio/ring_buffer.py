"""
Ring buffer for audio data storage

Stores the last N seconds of audio for context before wake word detection.

Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

from collections import deque
from threading import Lock
from typing import Optional


class AudioRingBuffer:
    """
    Thread-safe circular buffer for audio data.

    Stores the last N seconds of audio PCM16 data, allowing retrieval
    of context before a wake word is detected.
    """

    def __init__(self, max_seconds: int, sample_rate: int, channels: int = 1):
        """
        Initialize ring buffer

        Args:
            max_seconds: Maximum seconds of audio to store
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels
        """
        self.max_seconds = max_seconds
        self.sample_rate = sample_rate
        self.channels = channels

        # Calculate max bytes (16-bit = 2 bytes per sample)
        bytes_per_second = sample_rate * channels * 2
        self.max_bytes = max_seconds * bytes_per_second

        self._buffer: deque[bytes] = deque(maxlen=self.max_bytes)
        self._lock = Lock()
        self._total_bytes = 0

    def append(self, audio_data: bytes) -> None:
        """
        Append audio data to the buffer

        Args:
            audio_data: PCM16 audio bytes to append
        """
        with self._lock:
            for byte in audio_data:
                self._buffer.append(bytes([byte]))
            self._total_bytes += len(audio_data)

    def get_last_seconds(self, seconds: Optional[float] = None) -> bytes:
        """
        Get the last N seconds of audio

        Args:
            seconds: Number of seconds to retrieve (None = all available)

        Returns:
            PCM16 audio bytes
        """
        with self._lock:
            if not self._buffer:
                return b""

            if seconds is None:
                # Return all available data
                return b"".join(self._buffer)

            # Calculate how many bytes to retrieve
            bytes_per_second = self.sample_rate * self.channels * 2
            num_bytes = int(seconds * bytes_per_second)
            num_bytes = min(num_bytes, len(self._buffer))

            # Get the last num_bytes
            if num_bytes >= len(self._buffer):
                return b"".join(self._buffer)

            # Get from the end
            start_idx = len(self._buffer) - num_bytes
            return b"".join(list(self._buffer)[start_idx:])

    def get_all(self) -> bytes:
        """
        Get all buffered audio data

        Returns:
            All PCM16 audio bytes in buffer
        """
        return self.get_last_seconds(None)

    def clear(self) -> None:
        """Clear the buffer"""
        with self._lock:
            self._buffer.clear()
            self._total_bytes = 0

    def get_duration_seconds(self) -> float:
        """
        Get duration of currently buffered audio

        Returns:
            Duration in seconds
        """
        with self._lock:
            bytes_per_second = self.sample_rate * self.channels * 2
            return len(self._buffer) / bytes_per_second if bytes_per_second > 0 else 0

    def is_full(self) -> bool:
        """
        Check if buffer is at maximum capacity

        Returns:
            True if buffer is full
        """
        with self._lock:
            return len(self._buffer) >= self.max_bytes

    def __len__(self) -> int:
        """Get number of bytes in buffer"""
        with self._lock:
            return len(self._buffer)
