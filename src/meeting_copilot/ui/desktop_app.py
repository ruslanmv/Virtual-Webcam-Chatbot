"""
Desktop UI for Meeting Copilot

PySide6-based graphical interface for the meeting assistant.

Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

import sys
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MeetingCopilotUI(QMainWindow):
    """
    Main application window for Meeting Copilot
    """

    # Signals
    mute_toggled = Signal(bool)  # True = muted, False = listening
    mode_changed = Signal(str)  # answer/opinion/summarize
    audio_source_changed = Signal(str)  # microphone/system/both
    quit_requested = Signal()

    def __init__(self):
        super().__init__()

        self.is_muted = False
        self.is_listening = False

        self._init_ui()
        self._init_tray()

    def _init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Meeting Copilot - Watson")
        self.setMinimumSize(800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Header
        header = self._create_header()
        layout.addWidget(header)

        # Status indicator
        self.status_label = QLabel("🔴 Not Listening")
        self.status_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 10px;"
        )
        layout.addWidget(self.status_label)

        # Controls
        controls = self._create_controls()
        layout.addWidget(controls)

        # Transcript display
        transcript_group = QGroupBox("Live Transcript")
        transcript_layout = QVBoxLayout()
        self.transcript_display = QTextEdit()
        self.transcript_display.setReadOnly(True)
        self.transcript_display.setPlaceholderText(
            "Conversation transcript will appear here..."
        )
        transcript_layout.addWidget(self.transcript_display)
        transcript_group.setLayout(transcript_layout)
        layout.addWidget(transcript_group)

        # Response display
        response_group = QGroupBox("Watson's Response")
        response_layout = QVBoxLayout()
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        self.response_display.setPlaceholderText(
            "Watson's responses will appear here..."
        )
        response_layout.addWidget(self.response_display)
        response_group.setLayout(response_layout)
        layout.addWidget(response_group)

        # Footer
        footer = QLabel(
            "Developed by Ruslan Magana (contact@ruslanmv.com)"
        )
        footer.setStyleSheet("color: gray; padding: 5px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

    def _create_header(self) -> QWidget:
        """Create header widget"""
        header = QWidget()
        layout = QHBoxLayout()
        header.setLayout(layout)

        title = QLabel("🎙️ Meeting Copilot")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        layout.addStretch()

        return header

    def _create_controls(self) -> QWidget:
        """Create control panel"""
        controls = QGroupBox("Controls")
        layout = QVBoxLayout()
        controls.setLayout(layout)

        # Row 1: Audio source and mode
        row1 = QHBoxLayout()

        # Audio source selector
        row1.addWidget(QLabel("Audio Source:"))
        self.audio_source_combo = QComboBox()
        self.audio_source_combo.addItems(["Microphone", "System Audio", "Both"])
        self.audio_source_combo.currentTextChanged.connect(
            self._on_audio_source_changed
        )
        row1.addWidget(self.audio_source_combo)

        row1.addStretch()

        # Mode selector
        row1.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Answer", "Opinion", "Summarize"])
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        row1.addWidget(self.mode_combo)

        layout.addLayout(row1)

        # Row 2: Main buttons
        row2 = QHBoxLayout()

        # Mute/Unmute button
        self.mute_button = QPushButton("🔇 Mute")
        self.mute_button.setCheckable(True)
        self.mute_button.clicked.connect(self._on_mute_toggled)
        self.mute_button.setStyleSheet(
            """
            QPushButton {
                font-size: 14px;
                padding: 10px;
                min-width: 120px;
            }
            QPushButton:checked {
                background-color: #d32f2f;
                color: white;
            }
            """
        )
        row2.addWidget(self.mute_button)

        # Clear transcript button
        clear_button = QPushButton("🗑️ Clear")
        clear_button.clicked.connect(self._on_clear_clicked)
        row2.addWidget(clear_button)

        row2.addStretch()

        layout.addLayout(row2)

        return controls

    def _init_tray(self):
        """Initialize system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)

        # Create tray menu
        tray_menu = self.tray_icon.contextMenu() or self.tray_icon.setContextMenu(
            self.menuBar().addMenu("")
        )

        # Show/Hide action
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        # Mute/Unmute action
        self.tray_mute_action = QAction("Mute", self)
        self.tray_mute_action.triggered.connect(self._on_mute_toggled)
        tray_menu.addAction(self.tray_mute_action)

        tray_menu.addSeparator()

        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._on_quit)
        tray_menu.addAction(quit_action)

        # Set tray icon (would need an actual icon file)
        # For now, just show it
        self.tray_icon.show()

    @Slot()
    def _on_mute_toggled(self):
        """Handle mute button toggle"""
        self.is_muted = self.mute_button.isChecked()

        if self.is_muted:
            self.mute_button.setText("🔇 Unmute")
            self.status_label.setText("🔴 Muted")
            self.tray_mute_action.setText("Unmute")
        else:
            self.mute_button.setText("🔇 Mute")
            self.status_label.setText("🟢 Listening")
            self.tray_mute_action.setText("Mute")

        self.mute_toggled.emit(self.is_muted)

    @Slot(str)
    def _on_mode_changed(self, mode_text: str):
        """Handle mode change"""
        mode = mode_text.lower()
        self.mode_changed.emit(mode)

    @Slot(str)
    def _on_audio_source_changed(self, source_text: str):
        """Handle audio source change"""
        source_map = {
            "Microphone": "microphone",
            "System Audio": "system",
            "Both": "both",
        }
        source = source_map.get(source_text, "microphone")
        self.audio_source_changed.emit(source)

    @Slot()
    def _on_clear_clicked(self):
        """Clear transcript and response displays"""
        self.transcript_display.clear()
        self.response_display.clear()

    @Slot()
    def _on_quit(self):
        """Handle quit request"""
        self.quit_requested.emit()
        QApplication.quit()

    # Public methods for external control

    def add_transcript(self, text: str, is_wake: bool = False):
        """
        Add text to transcript display

        Args:
            text: Transcript text
            is_wake: True if this is a wake word trigger
        """
        if is_wake:
            self.transcript_display.append(f"<b>[WAKE] {text}</b>")
        else:
            self.transcript_display.append(text)

        # Auto-scroll to bottom
        self.transcript_display.verticalScrollBar().setValue(
            self.transcript_display.verticalScrollBar().maximum()
        )

    def set_response(self, text: str):
        """
        Set Watson's response

        Args:
            text: Response text
        """
        self.response_display.setPlainText(text)

    def append_response(self, text: str):
        """
        Append to Watson's response (for streaming)

        Args:
            text: Response text chunk
        """
        self.response_display.insertPlainText(text)

        # Auto-scroll to bottom
        self.response_display.verticalScrollBar().setValue(
            self.response_display.verticalScrollBar().maximum()
        )

    def set_listening_status(self, is_listening: bool):
        """
        Update listening status indicator

        Args:
            is_listening: True if actively listening
        """
        self.is_listening = is_listening

        if self.is_muted:
            self.status_label.setText("🔴 Muted")
        elif is_listening:
            self.status_label.setText("🟢 Listening")
        else:
            self.status_label.setText("⚪ Idle")

    def closeEvent(self, event):
        """Handle window close event"""
        # Minimize to tray instead of closing
        event.ignore()
        self.hide()


def create_app() -> tuple[QApplication, MeetingCopilotUI]:
    """
    Create and return Qt application and main window

    Returns:
        tuple: (app, window)
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Meeting Copilot")
    app.setOrganizationName("Ruslan Magana")

    window = MeetingCopilotUI()
    window.show()

    return app, window
