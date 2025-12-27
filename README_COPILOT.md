# 🎙️ Meeting Copilot

> AI-powered voice assistant for meetings with wake word detection, real-time transcription, and intelligent responses.

**Developed by:** Ruslan Magana
**Contact:** contact@ruslanmv.com

---

## ✨ Features

- 🎤 **Multi-source audio capture**: Microphone, system audio (meetings), or both
- 👂 **Voice Activity Detection (VAD)**: Intelligent speech segmentation
- 🔊 **Wake word activation**: Say "Watson" (configurable) to activate
- 📝 **Real-time transcription**: IBM Watson Speech-to-Text
- 🤖 **AI responses**: Powered by OpenAI GPT models
- 💬 **Multiple modes**: Answer questions, give opinions, or summarize discussions
- 🗣️ **Text-to-Speech**: Natural voice responses (Edge TTS or IBM Watson)
- 🖥️ **Desktop UI**: Professional PySide6 interface
- 🔒 **Privacy-first**: Opt-in logging with encryption
- ⚡ **Low latency**: < 2.5s wake-to-response target

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Windows** (recommended for system audio capture via WASAPI)
- **uv** package manager (auto-installed by Makefile)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/ruslanmv/Virtual-Webcam-Chatbot.git
cd Virtual-Webcam-Chatbot
```

2. **Install dependencies**

```bash
make install
```

This will:
- Install `uv` if not present
- Create a Python 3.11 virtual environment
- Install all required packages

3. **Configure API keys**

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required
IBM_SPEECH_TO_TEXT_API=your_ibm_stt_key
IBM_STT_URL=your_ibm_stt_url
OPENAI_API_KEY=your_openai_key

# Optional (Edge TTS is free and enabled by default)
TTS_PROVIDER=edge
```

**Get API keys:**
- **IBM Watson STT**: [IBM Cloud](https://cloud.ibm.com/catalog/services/speech-to-text)
- **OpenAI**: [OpenAI Platform](https://platform.openai.com/api-keys)

4. **Run the application**

```bash
make run
```

---

## 📖 Usage

### Makefile Commands

```bash
make help      # Show all available commands
make install   # Install dependencies with uv
make run       # Run the application (UI mode)
make console   # Run in console mode (no UI)
make dev       # Run in development mode
make test      # Run tests
make clean     # Clean up generated files
make lint      # Run code linting
make format    # Format code
```

### Running the Application

**UI Mode (default):**
```bash
make run
```

**Console Mode:**
```bash
make console
```

**With manual command:**
```bash
uv run python -m meeting_copilot.app
```

### Using the Assistant

1. **Start the application** (listening indicator will show green)
2. **Say the wake word**: "Watson" (or your configured bot name)
3. **Speak your request**:
   - "What did they say about the budget?"
   - "Give me your opinion on this approach"
   - "Summarize the last 2 minutes"
4. **Listen to Watson's response** (spoken and displayed)

### Modes

- **Answer Mode**: Responds to direct questions
- **Opinion Mode**: Provides analysis and perspective
- **Summarize Mode**: Condenses recent conversation

Change modes in the UI dropdown or configure `DEFAULT_MODE` in `.env`.

### Audio Sources

- **Microphone**: Capture your voice
- **System Audio**: Capture meeting audio (Zoom, Teams, etc.)
- **Both**: Capture both microphone and system audio

**Windows Setup for System Audio:**
1. Right-click speaker icon → "Sounds"
2. "Recording" tab → Enable "Stereo Mix"
3. Set as default or select in app

---

## 🏗️ Architecture

```
meeting_copilot/
├── audio/                 # Audio processing
│   ├── capture_mic.py    # Microphone capture
│   ├── capture_loopback.py # System audio capture
│   ├── vad.py            # Voice Activity Detection
│   └── ring_buffer.py    # Pre-wake audio buffer
├── stt/                   # Speech-to-Text
│   └── watson_stt.py     # IBM Watson STT client
├── wakeword/              # Wake word detection
│   └── wakeword_text.py  # Text-based wake detection
├── llm/                   # Language model
│   ├── client.py         # OpenAI client
│   └── prompts.py        # System prompts
├── tts/                   # Text-to-Speech
│   ├── edge_tts_client.py # Edge TTS (free)
│   └── ibm_tts.py        # IBM Watson TTS
├── ui/                    # User interface
│   └── desktop_app.py    # PySide6 UI
├── config.py             # Configuration management
└── app.py                # Main orchestrator
```

### Audio Pipeline

```
Microphone/System Audio
    ↓
Audio Capture (sounddevice)
    ↓
Ring Buffer (stores last 20s)
    ↓
VAD Segmentation (webrtcvad)
    ↓
Speech-to-Text (IBM Watson)
    ↓
Wake Word Detection (regex on transcript)
    ↓
LLM Processing (OpenAI)
    ↓
Text-to-Speech (Edge TTS)
    ↓
Speaker Output
```

---

## ⚙️ Configuration

### Environment Variables

All configuration is done via `.env` file. See `.env.example` for full options.

**Key Settings:**

```env
# Bot Configuration
BOT_NAME=watson                    # Wake word
AUDIO_SOURCE=microphone            # microphone/system/both
DEFAULT_MODE=answer                # answer/opinion/summarize

# Privacy
ENABLE_LOGGING=false               # Opt-in conversation logging
ENCRYPT_LOGS=true                  # Encrypt logs if enabled

# Performance
VAD_AGGRESSIVENESS=2               # 0-3 (higher = more aggressive)
PREWAKE_BUFFER_SECONDS=20         # Context window before wake
LATENCY_TARGET_MS=2500            # Response latency target
```

### TTS Provider

**Edge TTS (Free, Recommended):**
```env
TTS_PROVIDER=edge
EDGE_TTS_VOICE=en-US-GuyNeural
```

**IBM Watson TTS:**
```env
TTS_PROVIDER=ibm
IBM_TTS_API_KEY=your_key
IBM_TTS_URL=your_url
IBM_TTS_VOICE=en-US_AllisonV3Voice
```

---

## 🔒 Privacy & Compliance

### Non-Negotiable Principles

✅ **User Consent**: Explicit opt-in before audio capture
✅ **Visual Indicators**: Always show listening status
✅ **Mute Control**: Instant mute toggle + hotkey
✅ **Local-First**: Audio processed locally, only transcripts sent to APIs
✅ **Encryption**: Optional encrypted local logs
✅ **No Stealth**: Designed for transparent, consensual use

### Data Flow

1. **Audio Capture**: Stays local (not sent to cloud)
2. **Transcription**: Audio sent to IBM Watson STT
3. **LLM Processing**: Transcripts sent to OpenAI
4. **Logs**: Local storage only (opt-in, encrypted)

**No audio is stored** unless logging is explicitly enabled.

---

## 🛠️ Development

### Project Structure

- **Python 3.11**: Modern Python with type hints
- **uv**: Fast, reliable package management
- **PySide6**: Cross-platform Qt UI
- **Pydantic**: Settings validation
- **sounddevice**: Low-latency audio I/O

### Adding Dependencies

```bash
uv pip install <package>
uv pip freeze > requirements.txt
```

### Running Tests

```bash
make test
```

### Code Quality

```bash
make lint      # Check code
make format    # Auto-format
```

---

## 🐛 Troubleshooting

### "No loopback device found"

**Windows:**
1. Open Sound settings
2. Enable "Stereo Mix" in Recording devices
3. Restart application

**Linux/Mac:**
System audio capture is limited. Use virtual audio cable or microphone mode.

### "Watson STT error"

- Verify IBM Watson credentials in `.env`
- Check API key has STT permissions
- Test connection at IBM Cloud console

### "Low audio quality"

- Increase `VAD_AGGRESSIVENESS` (0-3)
- Adjust `VAD_PADDING_MS` for more context
- Use higher quality microphone

### "High latency"

- Switch to Edge TTS (`TTS_PROVIDER=edge`)
- Reduce `PREWAKE_BUFFER_SECONDS`
- Use faster OpenAI model (gpt-3.5-turbo)

---

## 📦 Building for Distribution

### Windows Installer (planned)

```bash
make build
```

Creates standalone installer with:
- Bundled Python runtime
- All dependencies
- Auto-update capability
- Desktop shortcuts

---

## 🗺️ Roadmap

### v1.0 (Current)
- ✅ Wake word detection (text-based)
- ✅ Multi-source audio capture
- ✅ Real-time transcription
- ✅ LLM responses
- ✅ TTS playback
- ✅ Desktop UI

### v1.1 (Planned)
- 🔲 Real keyword spotting (Porcupine/openWakeWord)
- 🔲 Virtual webcam overlay
- 🔲 Zoom/Teams integration
- 🔲 Custom wake words
- 🔲 Multi-language support

### v1.2 (Future)
- 🔲 Local LLM option (privacy mode)
- 🔲 Meeting analytics
- 🔲 Action item extraction
- 🔲 macOS/Linux support

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

Apache License 2.0 - see LICENSE file for details

---

## 👨‍💻 Author

**Ruslan Magana**
📧 contact@ruslanmv.com
🌐 [ruslanmv.com](https://ruslanmv.com)

---

## 🙏 Acknowledgments

- **IBM Watson**: Speech services
- **OpenAI**: Language models
- **Microsoft Edge**: Free TTS service
- **WebRTC VAD**: Voice activity detection

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ruslanmv/Virtual-Webcam-Chatbot/issues)
- **Email**: contact@ruslanmv.com
- **Documentation**: See `/docs` folder

---

**Built with ❤️ for better meetings**
