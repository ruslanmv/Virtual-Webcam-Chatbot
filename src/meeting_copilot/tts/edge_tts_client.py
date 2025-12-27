"""
Edge TTS client for text-to-speech

Uses Microsoft Edge's free TTS service for voice synthesis.

Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

import asyncio
import io
import tempfile
from typing import Optional

import edge_tts
from pydub import AudioSegment
from pydub.playback import play


class EdgeTTSClient:
    """
    Edge TTS client for text-to-speech.

    Uses Microsoft Edge's TTS service (free, no API key required).
    High quality and fast.
    """

    def __init__(self, voice: str = "en-US-GuyNeural"):
        """
        Initialize Edge TTS client

        Args:
            voice: Voice name (see list_voices for options)
        """
        self.voice = voice

    async def _synthesize_async(
        self,
        text: str,
        output_file: Optional[str] = None,
    ) -> bytes:
        """
        Synthesize speech asynchronously

        Args:
            text: Text to synthesize
            output_file: Optional output file path

        Returns:
            Audio bytes (MP3 format)
        """
        if output_file:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_file)

            # Read back the file
            with open(output_file, "rb") as f:
                return f.read()
        else:
            # Synthesize to bytes
            communicate = edge_tts.Communicate(text, self.voice)

            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            return audio_data

    def synthesize(
        self,
        text: str,
        output_file: Optional[str] = None,
    ) -> bytes:
        """
        Synthesize speech (sync wrapper)

        Args:
            text: Text to synthesize
            output_file: Optional output file path

        Returns:
            Audio bytes (MP3 format)
        """
        try:
            return asyncio.run(self._synthesize_async(text, output_file))
        except Exception as e:
            print(f"Edge TTS synthesis error: {e}")
            return b""

    def speak(self, text: str) -> None:
        """
        Synthesize and play speech

        Args:
            text: Text to speak
        """
        try:
            # Synthesize to temporary file
            with tempfile.NamedTemporaryFile(
                suffix=".mp3", delete=False
            ) as tmp_file:
                audio_data = self.synthesize(text, tmp_file.name)

                if audio_data:
                    # Load and play
                    audio = AudioSegment.from_mp3(tmp_file.name)
                    play(audio)
        except Exception as e:
            print(f"Edge TTS playback error: {e}")

    def speak_async(self, text: str) -> None:
        """
        Speak without blocking (runs in background)

        Args:
            text: Text to speak
        """
        import threading

        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()

    @staticmethod
    async def _list_voices_async() -> list[dict]:
        """
        List available voices asynchronously

        Returns:
            List of voice info dictionaries
        """
        voices = await edge_tts.list_voices()
        return [
            {
                "name": v["ShortName"],
                "gender": v["Gender"],
                "locale": v["Locale"],
            }
            for v in voices
        ]

    @staticmethod
    def list_voices() -> list[dict]:
        """
        List available voices

        Returns:
            List of voice info dictionaries
        """
        try:
            return asyncio.run(EdgeTTSClient._list_voices_async())
        except Exception as e:
            print(f"Error listing voices: {e}")
            return []

    @staticmethod
    def list_english_voices() -> list[str]:
        """
        List English voice names

        Returns:
            List of English voice names
        """
        voices = EdgeTTSClient.list_voices()
        return [
            v["name"]
            for v in voices
            if v["locale"].startswith("en-")
        ]

    def test_connection(self) -> bool:
        """
        Test TTS connection

        Returns:
            True if synthesis works
        """
        try:
            audio_data = self.synthesize("Test")
            return len(audio_data) > 0
        except Exception as e:
            print(f"Edge TTS connection test failed: {e}")
            return False
