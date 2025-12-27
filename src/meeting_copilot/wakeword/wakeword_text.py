"""
Text-based wake word detection

Detects wake word in transcribed text (simple v1 approach).

Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

import re
from typing import Optional


class TextWakeWord:
    """
    Text-based wake word detector.

    Searches for the bot name in transcribed text to trigger
    assistant activation. Simple but effective for v1.
    """

    def __init__(self, bot_name: str):
        """
        Initialize wake word detector

        Args:
            bot_name: Wake word / bot name (case-insensitive)
        """
        self.bot_name = bot_name.lower().strip()

        # Create regex pattern for word boundary matching
        # This prevents false triggers like "watson" in "Waterston"
        escaped_name = re.escape(self.bot_name)
        self.pattern = re.compile(
            rf"\b{escaped_name}\b",
            re.IGNORECASE
        )

        # Alternative patterns (common variations)
        self._alt_patterns = self._generate_alternatives()

    def _generate_alternatives(self) -> list[re.Pattern]:
        """
        Generate alternative wake word patterns

        Handles common STT transcription errors.

        Returns:
            List of compiled regex patterns
        """
        alternatives = []

        # Common mishearings for "watson"
        if self.bot_name == "watson":
            alt_names = ["whatson", "what's on", "watt son", "wadson"]
            for alt in alt_names:
                escaped = re.escape(alt)
                alternatives.append(
                    re.compile(rf"\b{escaped}\b", re.IGNORECASE)
                )

        return alternatives

    def is_wake(self, transcript: str) -> bool:
        """
        Check if transcript contains wake word

        Args:
            transcript: Transcribed text

        Returns:
            True if wake word detected
        """
        if not transcript:
            return False

        # Check primary pattern
        if self.pattern.search(transcript):
            return True

        # Check alternative patterns
        for alt_pattern in self._alt_patterns:
            if alt_pattern.search(transcript):
                return True

        return False

    def extract_command(self, transcript: str) -> Optional[str]:
        """
        Extract command text after wake word

        Args:
            transcript: Transcribed text

        Returns:
            Command text or None if no wake word
        """
        if not self.is_wake(transcript):
            return None

        # Find wake word position
        match = self.pattern.search(transcript)
        if not match:
            # Try alternatives
            for alt_pattern in self._alt_patterns:
                match = alt_pattern.search(transcript)
                if match:
                    break

        if not match:
            return None

        # Extract everything after the wake word
        command_start = match.end()
        command = transcript[command_start:].strip()

        # Remove common filler words at the start
        fillers = ["um", "uh", "so", "please", "could you", "can you"]
        for filler in fillers:
            if command.lower().startswith(filler):
                command = command[len(filler):].strip()

        return command if command else None

    def get_wake_position(self, transcript: str) -> Optional[int]:
        """
        Get character position of wake word in transcript

        Args:
            transcript: Transcribed text

        Returns:
            Character index or None
        """
        match = self.pattern.search(transcript)
        if match:
            return match.start()

        # Try alternatives
        for alt_pattern in self._alt_patterns:
            match = alt_pattern.search(transcript)
            if match:
                return match.start()

        return None

    def __repr__(self) -> str:
        return f"TextWakeWord(bot_name='{self.bot_name}')"
