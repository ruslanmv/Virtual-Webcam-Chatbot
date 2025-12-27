"""
Meeting Copilot - Main Application

Voice assistant for meetings with wake word detection, STT, LLM, and TTS.

Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

import argparse
import queue
import sys
import threading
import time
from collections import deque
from typing import Optional

from PySide6.QtCore import QTimer

from meeting_copilot.audio.capture_loopback import LoopbackCapture
from meeting_copilot.audio.capture_mic import MicrophoneCapture
from meeting_copilot.audio.ring_buffer import AudioRingBuffer
from meeting_copilot.audio.vad import VADSegmenter
from meeting_copilot.config import get_secrets, get_settings, validate_configuration
from meeting_copilot.llm.client import LLMClient
from meeting_copilot.stt.watson_stt import WatsonSTT
from meeting_copilot.tts.edge_tts_client import EdgeTTSClient
from meeting_copilot.tts.ibm_tts import IBMWatsonTTS
from meeting_copilot.ui.desktop_app import create_app
from meeting_copilot.wakeword.wakeword_text import TextWakeWord


class MeetingCopilotApp:
    """
    Main Meeting Copilot application.

    Orchestrates audio capture, VAD, STT, wake word detection,
    LLM responses, and TTS output.
    """

    def __init__(self, console_mode: bool = False):
        """
        Initialize Meeting Copilot

        Args:
            console_mode: Run in console mode (no UI)
        """
        self.console_mode = console_mode

        # Load configuration
        self.settings = get_settings()
        self.secrets = get_secrets()

        # Validate configuration
        is_valid, errors = validate_configuration()
        if not is_valid:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

        print("✅ Configuration loaded successfully")

        # Initialize components
        self._init_components()

        # State
        self.is_running = False
        self.is_muted = False
        self.current_mode = self.settings.default_mode

        # Transcript history
        self.transcript_history: deque[str] = deque(maxlen=50)

        # Audio queue
        self.audio_queue: queue.Queue[bytes] = queue.Queue(maxsize=200)

        # UI components (if not console mode)
        self.ui_app = None
        self.ui_window = None

    def _init_components(self):
        """Initialize all components"""
        print("🔧 Initializing components...")

        # Speech-to-Text
        self.stt = WatsonSTT(
            api_key=self.secrets.ibm_stt_api_key,
            url=self.secrets.ibm_stt_url,
            model=self.secrets.ibm_stt_model,
        )
        print("  ✓ Watson STT initialized")

        # Wake word detector
        self.wake_word = TextWakeWord(self.settings.bot_name)
        print(f"  ✓ Wake word detector initialized ('{self.settings.bot_name}')")

        # LLM client (multi-provider support with watsonx.ai as default)
        self.llm = LLMClient()
        # Initialization message printed by LLMClient

        # Text-to-Speech
        if self.secrets.tts_provider == "ibm":
            self.tts = IBMWatsonTTS(
                api_key=self.secrets.ibm_tts_api_key,
                url=self.secrets.ibm_tts_url,
                voice=self.secrets.ibm_tts_voice,
            )
            print("  ✓ IBM Watson TTS initialized")
        else:
            self.tts = EdgeTTSClient(voice=self.secrets.edge_tts_voice)
            print("  ✓ Edge TTS initialized")

        # Audio ring buffer
        self.ring_buffer = AudioRingBuffer(
            max_seconds=self.settings.prewake_buffer_seconds,
            sample_rate=self.settings.sample_rate,
            channels=self.settings.channels,
        )
        print("  ✓ Audio ring buffer initialized")

        # VAD segmenter
        self.vad = VADSegmenter(
            sample_rate=self.settings.sample_rate,
            aggressiveness=self.settings.vad_aggressiveness,
            frame_ms=self.settings.vad_frame_ms,
            padding_ms=self.settings.vad_padding_ms,
        )
        print("  ✓ VAD segmenter initialized")

        # Audio capture (will be started later)
        self.mic_capture: Optional[MicrophoneCapture] = None
        self.loopback_capture: Optional[LoopbackCapture] = None

    def _start_audio_capture(self):
        """Start audio capture based on settings"""
        audio_source = self.settings.audio_source

        if audio_source in ("microphone", "both"):
            print("🎤 Starting microphone capture...")
            self.mic_capture = MicrophoneCapture(
                sample_rate=self.settings.sample_rate,
                channels=self.settings.channels,
                chunk_size=self.settings.chunk_size,
            )
            self.mic_capture.start(callback=self._on_audio_data)
            print("  ✓ Microphone capture started")

        if audio_source in ("system", "both"):
            print("🔊 Starting system audio capture...")
            try:
                self.loopback_capture = LoopbackCapture(
                    sample_rate=self.settings.sample_rate,
                    channels=self.settings.channels,
                    chunk_size=self.settings.chunk_size,
                )
                self.loopback_capture.start(callback=self._on_audio_data)
                print("  ✓ System audio capture started")
            except Exception as e:
                print(f"  ⚠️ Could not start system audio capture: {e}")
                print("  ℹ️ Enable 'Stereo Mix' in Windows recording devices")

    def _stop_audio_capture(self):
        """Stop audio capture"""
        if self.mic_capture:
            self.mic_capture.stop()
            self.mic_capture = None

        if self.loopback_capture:
            self.loopback_capture.stop()
            self.loopback_capture = None

    def _on_audio_data(self, pcm_bytes: bytes):
        """
        Callback for audio data

        Args:
            pcm_bytes: PCM16 audio bytes
        """
        if self.is_muted:
            return

        # Add to ring buffer
        self.ring_buffer.append(pcm_bytes)

        # Add to audio queue for processing
        try:
            self.audio_queue.put_nowait(pcm_bytes)
        except queue.Full:
            pass  # Drop frame if queue is full

    def _audio_processing_thread(self):
        """Audio processing thread (VAD + STT + wake word detection)"""
        print("🎯 Audio processing thread started")

        while self.is_running:
            try:
                # Get audio data
                pcm_data = self.audio_queue.get(timeout=0.1)

                # Process through VAD
                for utterance in self.vad.process_audio(pcm_data):
                    # Transcribe utterance
                    transcript, confidence = self.stt.transcribe_pcm16(
                        utterance, self.settings.sample_rate
                    )

                    if not transcript:
                        continue

                    # Add to history
                    self.transcript_history.append(transcript)

                    # Update UI or print
                    self._on_transcript(transcript, confidence)

                    # Check for wake word
                    if self.wake_word.is_wake(transcript):
                        self._on_wake_detected(transcript)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in audio processing: {e}")

        print("🎯 Audio processing thread stopped")

    def _on_transcript(self, transcript: str, confidence: float):
        """
        Handle new transcript

        Args:
            transcript: Transcribed text
            confidence: Confidence score
        """
        if self.console_mode:
            print(f"📝 [{confidence:.2f}] {transcript}")
        else:
            if self.ui_window:
                self.ui_window.add_transcript(transcript)

    def _on_wake_detected(self, transcript: str):
        """
        Handle wake word detection

        Args:
            transcript: Transcript containing wake word
        """
        print(f"\n🔔 WAKE WORD DETECTED: {transcript}")

        if not self.console_mode and self.ui_window:
            self.ui_window.add_transcript(transcript, is_wake=True)

        # Get context from ring buffer
        context_audio = self.ring_buffer.get_last_seconds(
            self.settings.prewake_buffer_seconds
        )

        # Build context from transcript history
        context_text = "\n".join(list(self.transcript_history)[-10:])

        # Generate LLM response
        print("🤖 Generating response...")
        response = self.llm.respond(
            mode=self.current_mode,
            transcript_context=context_text,
        )

        print(f"💬 Watson: {response}\n")

        # Update UI
        if not self.console_mode and self.ui_window:
            self.ui_window.set_response(response)

        # Speak response
        print("🔊 Speaking response...")
        self.tts.speak_async(response)

    def run_console(self):
        """Run in console mode"""
        print("\n" + "=" * 60)
        print("🎙️  Meeting Copilot - Console Mode")
        print("=" * 60)
        print(f"Wake word: '{self.settings.bot_name}'")
        print(f"Mode: {self.current_mode}")
        print(f"Audio source: {self.settings.audio_source}")
        print("=" * 60)
        print("\nListening... (Press Ctrl+C to quit)\n")

        self.is_running = True

        # Start audio capture
        self._start_audio_capture()

        # Start processing thread
        processing_thread = threading.Thread(
            target=self._audio_processing_thread,
            daemon=True,
        )
        processing_thread.start()

        try:
            # Keep running
            while self.is_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down...")
            self.is_running = False
            self._stop_audio_capture()

    def run_ui(self):
        """Run with graphical UI"""
        print("\n🖥️  Starting UI mode...")

        # Create Qt application
        self.ui_app, self.ui_window = create_app()

        # Connect UI signals
        self.ui_window.mute_toggled.connect(self._on_ui_mute_toggled)
        self.ui_window.mode_changed.connect(self._on_ui_mode_changed)
        self.ui_window.audio_source_changed.connect(self._on_ui_audio_source_changed)
        self.ui_window.quit_requested.connect(self._on_ui_quit)

        # Start audio processing
        self.is_running = True
        self._start_audio_capture()

        # Start processing thread
        processing_thread = threading.Thread(
            target=self._audio_processing_thread,
            daemon=True,
        )
        processing_thread.start()

        # Update listening status
        self.ui_window.set_listening_status(True)

        # Run Qt event loop
        sys.exit(self.ui_app.exec())

    def _on_ui_mute_toggled(self, is_muted: bool):
        """Handle UI mute toggle"""
        self.is_muted = is_muted
        print(f"🔇 Mute: {is_muted}")

    def _on_ui_mode_changed(self, mode: str):
        """Handle UI mode change"""
        self.current_mode = mode
        print(f"🎯 Mode changed to: {mode}")

    def _on_ui_audio_source_changed(self, source: str):
        """Handle UI audio source change"""
        print(f"🎤 Audio source changed to: {source}")
        # TODO: Restart audio capture with new source

    def _on_ui_quit(self):
        """Handle UI quit request"""
        print("\n👋 Shutting down...")
        self.is_running = False
        self._stop_audio_capture()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Meeting Copilot Voice Assistant")
    parser.add_argument(
        "--console",
        action="store_true",
        help="Run in console mode (no UI)",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Development mode",
    )

    args = parser.parse_args()

    # Print banner
    print("\n" + "=" * 60)
    print("🎙️  Meeting Copilot v1.0.0")
    print("Developed by: Ruslan Magana (contact@ruslanmv.com)")
    print("=" * 60 + "\n")

    # Create and run app
    app = MeetingCopilotApp(console_mode=args.console)

    if args.console:
        app.run_console()
    else:
        app.run_ui()


if __name__ == "__main__":
    main()
