"""
Voice Activity Detection (VAD) using WebRTC VAD

Segments continuous audio stream into speech utterances.

Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

from collections import deque
from typing import Iterator, Optional

import webrtcvad


class VADSegmenter:
    """
    Voice Activity Detection segmenter.

    Processes continuous audio stream and yields complete utterances
    when speech ends (with configurable padding).
    """

    def __init__(
        self,
        sample_rate: int,
        aggressiveness: int = 2,
        frame_ms: int = 30,
        padding_ms: int = 300,
    ):
        """
        Initialize VAD segmenter

        Args:
            sample_rate: Audio sample rate in Hz (8000, 16000, 32000, or 48000)
            aggressiveness: VAD aggressiveness (0-3, higher = more aggressive)
            frame_ms: Frame duration in ms (10, 20, or 30)
            padding_ms: Silence padding in ms before/after speech
        """
        if sample_rate not in (8000, 16000, 32000, 48000):
            raise ValueError(
                f"Sample rate must be 8000, 16000, 32000, or 48000 (got {sample_rate})"
            )

        if frame_ms not in (10, 20, 30):
            raise ValueError(f"Frame duration must be 10, 20, or 30 ms (got {frame_ms})")

        if not 0 <= aggressiveness <= 3:
            raise ValueError(
                f"Aggressiveness must be 0-3 (got {aggressiveness})"
            )

        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.padding_ms = padding_ms

        # Calculate frame size in bytes (16-bit PCM = 2 bytes per sample)
        self.frame_bytes = int(sample_rate * (frame_ms / 1000.0) * 2)

        # Calculate padding in frames
        self.padding_frames = int(padding_ms / frame_ms)

        # Ring buffer for padding
        self.ring: deque[tuple[bytes, bool]] = deque(maxlen=self.padding_frames)

        # Current utterance state
        self.triggered = False
        self._current_utterance: list[bytes] = []

    def process_audio(self, pcm_data: bytes) -> Iterator[bytes]:
        """
        Process audio data and yield complete utterances

        Args:
            pcm_data: PCM16 mono audio bytes

        Yields:
            Complete utterance audio bytes when speech ends
        """
        # Split audio into exact VAD frame sizes
        for i in range(0, len(pcm_data) - self.frame_bytes + 1, self.frame_bytes):
            frame = pcm_data[i : i + self.frame_bytes]

            # Ensure frame is exact size
            if len(frame) != self.frame_bytes:
                continue

            yield from self._process_frame(frame)

    def _process_frame(self, frame: bytes) -> Iterator[bytes]:
        """
        Process a single audio frame

        Args:
            frame: Audio frame (must be exact frame_bytes size)

        Yields:
            Complete utterance when speech ends
        """
        # Detect speech in frame
        try:
            is_speech = self.vad.is_speech(frame, self.sample_rate)
        except Exception:
            # Invalid frame, skip
            return

        if not self.triggered:
            # Not currently in speech - check if we should start
            self.ring.append((frame, is_speech))

            # Count voiced frames in ring buffer
            num_voiced = sum(1 for _, speech in self.ring if speech)

            # If enough voiced frames, start utterance
            if num_voiced > 0.6 * self.ring.maxlen:
                self.triggered = True

                # Start utterance with buffered audio
                voiced_frames = b"".join(f for f, _ in self.ring)
                self.ring.clear()
                self._current_utterance = [voiced_frames]

        else:
            # Currently in speech
            self._current_utterance.append(frame)
            self.ring.append((frame, is_speech))

            # Count unvoiced frames in ring buffer
            num_unvoiced = sum(1 for _, speech in self.ring if not speech)

            # If enough silence, end utterance
            if num_unvoiced > 0.8 * self.ring.maxlen:
                # Complete utterance
                utterance = b"".join(self._current_utterance)

                # Reset state
                self._current_utterance = []
                self.ring.clear()
                self.triggered = False

                # Yield complete utterance
                yield utterance

    def flush(self) -> Optional[bytes]:
        """
        Flush any pending utterance

        Returns:
            Pending utterance bytes or None
        """
        if self._current_utterance:
            utterance = b"".join(self._current_utterance)
            self._current_utterance = []
            self.triggered = False
            self.ring.clear()
            return utterance
        return None

    def reset(self) -> None:
        """Reset VAD state"""
        self._current_utterance = []
        self.triggered = False
        self.ring.clear()

    @property
    def is_speaking(self) -> bool:
        """Check if currently in a speech segment"""
        return self.triggered
