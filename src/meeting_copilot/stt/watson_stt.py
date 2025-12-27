"""
IBM Watson Speech-to-Text client

Transcribes audio using IBM Watson STT service.

Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

import io
import wave
from typing import Optional

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import SpeechToTextV1


class WatsonSTT:
    """
    IBM Watson Speech-to-Text client.

    Provides audio transcription using IBM Watson's cloud STT service.
    """

    def __init__(
        self,
        api_key: str,
        url: str,
        model: str = "en-US_BroadbandModel",
    ):
        """
        Initialize Watson STT client

        Args:
            api_key: IBM Watson API key
            url: IBM Watson service URL
            model: STT model to use

        Raises:
            ValueError: If credentials are missing
        """
        if not api_key or not url:
            raise ValueError(
                "Missing IBM Watson STT credentials (api_key, url)"
            )

        # Create authenticator and client
        authenticator = IAMAuthenticator(api_key)
        self.client = SpeechToTextV1(authenticator=authenticator)
        self.client.set_service_url(url)

        self.model = model

    def transcribe_pcm16(
        self,
        pcm_bytes: bytes,
        sample_rate: int,
        channels: int = 1,
    ) -> tuple[str, float]:
        """
        Transcribe PCM16 audio data

        Args:
            pcm_bytes: PCM16 audio bytes
            sample_rate: Sample rate in Hz
            channels: Number of channels

        Returns:
            tuple: (transcript_text, confidence)
        """
        if not pcm_bytes:
            return "", 0.0

        # Watson expects WAV format, so wrap PCM in WAV container
        wav_bytes = self._pcm_to_wav(pcm_bytes, sample_rate, channels)

        # Transcribe
        try:
            response = self.client.recognize(
                audio=wav_bytes,
                content_type="audio/wav",
                model=self.model,
                timestamps=False,
                word_confidence=False,
                max_alternatives=1,
            ).get_result()

            # Extract transcript
            results = response.get("results", [])
            if not results:
                return "", 0.0

            # Get best alternative
            alternative = results[0]["alternatives"][0]
            transcript = alternative.get("transcript", "").strip()
            confidence = alternative.get("confidence", 0.0)

            return transcript, confidence

        except Exception as e:
            print(f"Watson STT error: {e}")
            return "", 0.0

    def transcribe_file(
        self,
        file_path: str,
    ) -> tuple[str, float]:
        """
        Transcribe audio file

        Args:
            file_path: Path to audio file (WAV, MP3, etc.)

        Returns:
            tuple: (transcript_text, confidence)
        """
        try:
            with open(file_path, "rb") as audio_file:
                response = self.client.recognize(
                    audio=audio_file,
                    content_type=self._get_content_type(file_path),
                    model=self.model,
                    timestamps=False,
                    word_confidence=False,
                    max_alternatives=1,
                ).get_result()

            # Extract transcript
            results = response.get("results", [])
            if not results:
                return "", 0.0

            alternative = results[0]["alternatives"][0]
            transcript = alternative.get("transcript", "").strip()
            confidence = alternative.get("confidence", 0.0)

            return transcript, confidence

        except Exception as e:
            print(f"Watson STT file error: {e}")
            return "", 0.0

    @staticmethod
    def _pcm_to_wav(
        pcm_bytes: bytes,
        sample_rate: int,
        channels: int = 1,
    ) -> bytes:
        """
        Convert PCM16 bytes to WAV format

        Args:
            pcm_bytes: PCM16 audio bytes
            sample_rate: Sample rate in Hz
            channels: Number of channels

        Returns:
            WAV file bytes
        """
        wav_buffer = io.BytesIO()

        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(2)  # 16-bit = 2 bytes
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_bytes)

        wav_buffer.seek(0)
        return wav_buffer.read()

    @staticmethod
    def _get_content_type(file_path: str) -> str:
        """
        Get content type from file extension

        Args:
            file_path: Path to audio file

        Returns:
            Content type string
        """
        file_path_lower = file_path.lower()

        if file_path_lower.endswith(".wav"):
            return "audio/wav"
        elif file_path_lower.endswith(".mp3"):
            return "audio/mp3"
        elif file_path_lower.endswith(".flac"):
            return "audio/flac"
        elif file_path_lower.endswith(".ogg"):
            return "audio/ogg"
        else:
            # Default to WAV
            return "audio/wav"

    def test_connection(self) -> bool:
        """
        Test Watson STT connection

        Returns:
            True if connection successful
        """
        try:
            # List available models as a connection test
            models = self.client.list_models().get_result()
            return len(models.get("models", [])) > 0
        except Exception as e:
            print(f"Watson STT connection test failed: {e}")
            return False
