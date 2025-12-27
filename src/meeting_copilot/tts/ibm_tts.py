"""
IBM Watson Text-to-Speech client

Uses IBM Watson TTS service for voice synthesis.

Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

import tempfile
from typing import Optional

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import TextToSpeechV1
from pydub import AudioSegment
from pydub.playback import play


class IBMWatsonTTS:
    """
    IBM Watson Text-to-Speech client.

    Provides high-quality voice synthesis using IBM Watson cloud service.
    """

    def __init__(
        self,
        api_key: str,
        url: str,
        voice: str = "en-US_AllisonV3Voice",
    ):
        """
        Initialize IBM Watson TTS client

        Args:
            api_key: IBM Watson API key
            url: IBM Watson service URL
            voice: Voice name to use

        Raises:
            ValueError: If credentials are missing
        """
        if not api_key or not url:
            raise ValueError("Missing IBM Watson TTS credentials (api_key, url)")

        # Create authenticator and client
        authenticator = IAMAuthenticator(api_key)
        self.client = TextToSpeechV1(authenticator=authenticator)
        self.client.set_service_url(url)

        self.voice = voice

    def synthesize(
        self,
        text: str,
        output_file: Optional[str] = None,
        audio_format: str = "audio/mp3",
    ) -> bytes:
        """
        Synthesize speech

        Args:
            text: Text to synthesize
            output_file: Optional output file path
            audio_format: Audio format (audio/mp3, audio/wav, etc.)

        Returns:
            Audio bytes
        """
        try:
            response = self.client.synthesize(
                text=text,
                voice=self.voice,
                accept=audio_format,
            ).get_result()

            # Get audio content
            audio_data = response.content

            # Save to file if requested
            if output_file:
                with open(output_file, "wb") as f:
                    f.write(audio_data)

            return audio_data

        except Exception as e:
            print(f"IBM Watson TTS synthesis error: {e}")
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
            print(f"IBM Watson TTS playback error: {e}")

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

    def list_voices(self) -> list[dict]:
        """
        List available voices

        Returns:
            List of voice info dictionaries
        """
        try:
            response = self.client.list_voices().get_result()
            voices = response.get("voices", [])

            return [
                {
                    "name": v["name"],
                    "language": v["language"],
                    "gender": v["gender"],
                    "description": v.get("description", ""),
                }
                for v in voices
            ]
        except Exception as e:
            print(f"Error listing voices: {e}")
            return []

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
            print(f"IBM Watson TTS connection test failed: {e}")
            return False
