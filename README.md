<div align="center">

# 🎙️ Meeting Copilot

### Enterprise AI Voice Assistant for Intelligent Meeting Support

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/ruslanmv/Virtual-Webcam-Chatbot)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](https://github.com/ruslanmv/Virtual-Webcam-Chatbot)

**Transform your meetings with AI-powered voice assistance**

[Features](#-key-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Architecture](#-architecture) • [Support](#-support)

---

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [API Integration](#-api-integration)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🌟 Overview

**Meeting Copilot** is an enterprise-grade AI voice assistant designed to enhance productivity during meetings. It provides real-time transcription, intelligent responses, and meeting summaries through advanced speech recognition and natural language processing.

### 🎯 Perfect For

- 💼 **Business Professionals** - Never miss important meeting details
- 👥 **Remote Teams** - Stay engaged in virtual meetings
- 📊 **Project Managers** - Capture action items automatically
- 🎓 **Educators** - Assist in virtual classrooms
- 🏢 **Enterprises** - Scalable meeting intelligence solution

---

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🎤 Audio Intelligence
- **Multi-source Capture** - Microphone, system audio, or both
- **Voice Activity Detection** - Smart speech segmentation
- **Real-time Transcription** - IBM Watson STT integration
- **Wake Word Activation** - Customizable trigger ("Watson")

</td>
<td width="50%">

### 🤖 AI-Powered
- **Multi-Provider LLM** - IBM watsonx.ai (default), OpenAI, Claude, Ollama
- **Contextual Responses** - Answer, Opinion, Summarize modes
- **Text-to-Speech** - Natural voice output
- **Conversation Memory** - Context-aware interactions

</td>
</tr>
<tr>
<td width="50%">

### 🖥️ Professional Interface
- **Desktop Application** - Modern PySide6 UI
- **Real-time Display** - Live transcript visualization
- **System Tray** - Minimalist operation
- **Hotkeys** - Quick mute/unmute controls

</td>
<td width="50%">

### 🔒 Privacy & Security
- **Opt-in Logging** - User consent required
- **Data Encryption** - Secure local storage
- **Privacy-First** - No unauthorized recording
- **Compliance Ready** - Enterprise data policies

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2B-0078D6?logo=windows&logoColor=white)
![uv](https://img.shields.io/badge/uv-Package%20Manager-orange)

### One-Command Installation

```bash
# Clone repository
git clone https://github.com/ruslanmv/Virtual-Webcam-Chatbot.git
cd Virtual-Webcam-Chatbot

# Install with uv (auto-installs if missing)
make install

# Configure API keys
cp .env.example .env
# Edit .env with your credentials

# Launch application
make run
```

### ⚡ That's It!

Your Meeting Copilot is now ready. Say **"Watson"** to activate!

---

## 📦 Installation

### Method 1: Using Makefile (Recommended)

```bash
make install
```

This will:
- ✅ Install `uv` package manager (if not present)
- ✅ Create Python 3.11 virtual environment
- ✅ Install all dependencies
- ✅ Verify installation

### Method 2: Manual Installation

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv --python 3.11

# Install package
uv pip install -e .
```

### Verify Installation

```bash
make info
```

---

## ⚙️ Configuration

### 1. API Keys Setup

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Required Credentials

Edit `.env` and add your API keys:

```env
# IBM Watson Speech-to-Text (Required)
IBM_SPEECH_TO_TEXT_API=your_ibm_stt_api_key
IBM_STT_URL=https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/xxx

# LLM Provider (Default: watsonx.ai)
LLM_PROVIDER=watsonx

# IBM watsonx.ai (Default LLM - Required)
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_PROJECT_ID=your_watsonx_project_id
WATSONX_MODEL_ID=meta-llama/llama-3-3-70b-instruct
WATSONX_BASE_URL=https://us-south.ml.cloud.ibm.com

# Alternative LLM Providers (Optional)
# OpenAI: Uncomment and configure if using LLM_PROVIDER=openai
# OPENAI_API_KEY=your_openai_api_key
# OPENAI_MODEL=gpt-4o-mini

# TTS Provider (Edge TTS is free - no key needed)
TTS_PROVIDER=edge
EDGE_TTS_VOICE=en-US-GuyNeural
```

### 3. Get API Keys

| Service | Purpose | Get Key |
|---------|---------|---------|
| 🔊 **IBM Watson STT** | Speech-to-Text | [IBM Cloud Console](https://cloud.ibm.com/catalog/services/speech-to-text) |
| 🤖 **IBM watsonx.ai** | Language Model (Default) | [IBM Cloud Console](https://cloud.ibm.com/catalog/services/watsonx-ai) |
| 🤖 **OpenAI** | Alternative LLM | [OpenAI Platform](https://platform.openai.com/api-keys) |
| 🤖 **Anthropic Claude** | Alternative LLM | [Anthropic Console](https://console.anthropic.com/) |
| 🗣️ **Edge TTS** | Text-to-Speech | Free - No key required |

### 4. Optional Settings

```env
# Bot Configuration
BOT_NAME=watson                    # Change wake word
AUDIO_SOURCE=microphone            # microphone/system/both
DEFAULT_MODE=answer                # answer/opinion/summarize

# Privacy
ENABLE_LOGGING=false               # Opt-in conversation logging
ENCRYPT_LOGS=true                  # Encrypt logs if enabled

# Performance
VAD_AGGRESSIVENESS=2               # 0-3 (higher = more aggressive)
PREWAKE_BUFFER_SECONDS=20         # Context window before wake
```

---

## 💻 Usage

### Launch Application

```bash
# Desktop UI (default)
make run

# Console mode (no UI)
make console

# Development mode
make dev
```

### Using the Assistant

1. **▶️ Start Application** - Launch with `make run`
2. **🟢 Listening** - Green indicator shows active state
3. **🗣️ Say Wake Word** - "Watson" (or your configured name)
4. **💬 Speak Request** - Ask questions or request summaries
5. **👂 Hear Response** - AI responds with spoken answer

### Example Interactions

```
You: "Watson, what did they say about the Q4 budget?"
Watson: "The team discussed a 15% increase in Q4 budget allocation..."

You: "Watson, give me your opinion on this approach"
Watson: "Based on the discussion, this approach has merit because..."

You: "Watson, summarize the last 2 minutes"
Watson: "Key points: 1) Budget approval pending, 2) Timeline extended..."
```

### Assistant Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| 💬 **Answer** | Direct question responses | "What did they say about X?" |
| 💡 **Opinion** | Analysis and perspective | "What do you think about Y?" |
| 📝 **Summarize** | Conversation summary | "Summarize the discussion" |

### Keyboard Shortcuts

| Action | Shortcut | Description |
|--------|----------|-------------|
| 🔇 **Mute/Unmute** | Button | Toggle listening |
| 🗑️ **Clear** | Button | Clear transcript |
| ❌ **Quit** | Tray → Quit | Close application |

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐
│  🎤 Microphone  │────┐
└─────────────────┘    │
                       ▼
┌─────────────────┐  ┌────────────────┐
│ 🔊 System Audio │─▶│ Audio Capture  │
└─────────────────┘  └────────┬───────┘
                              ▼
                     ┌────────────────┐
                     │ VAD Segment    │
                     └────────┬───────┘
                              ▼
                     ┌────────────────┐
                     │  Ring Buffer   │
                     └────────┬───────┘
                              ▼
                     ┌────────────────┐
                     │  Watson STT    │
                     └────────┬───────┘
                              ▼
                     ┌────────────────┐
                     │  Wake Word?    │
                     └────┬──────┬────┘
                         Yes    No
                          ▼      └──────┐
                   ┌──────────┐         │
                   │ watsonx  │         │
                   │   LLM    │         │
                   └────┬─────┘         │
                        ▼               │
                   ┌──────────┐         │
                   │   TTS    │         │
                   └────┬─────┘         │
                        ▼               │
              ┌──────────────────┐     │
              │ 🔊 Speaker + UI  │◀────┘
              └──────────────────┘
```

### Component Structure

```
meeting_copilot/
├── 🎵 audio/              Audio Processing Pipeline
│   ├── capture_mic.py     Microphone capture (sounddevice)
│   ├── capture_loopback.py System audio (WASAPI)
│   ├── vad.py             Voice Activity Detection (WebRTC)
│   └── ring_buffer.py     Pre-wake audio buffer
│
├── 🗣️ stt/               Speech-to-Text
│   └── watson_stt.py      IBM Watson STT client
│
├── 🎯 wakeword/           Wake Word Detection
│   └── wakeword_text.py   Text-based detection (v1.0)
│
├── 🤖 llm/               Language Model
│   ├── client.py          Multi-provider LLM client (watsonx/OpenAI/Claude/Ollama)
│   ├── model_catalog.py   Model discovery for all providers
│   └── prompts.py         System prompts & templates
│
├── 🔊 tts/               Text-to-Speech
│   ├── edge_tts_client.py Microsoft Edge TTS (free)
│   └── ibm_tts.py         IBM Watson TTS
│
├── 🖥️ ui/                User Interface
│   └── desktop_app.py     PySide6 desktop application
│
├── ⚙️ config.py           Configuration management
└── 🚀 app.py              Main orchestrator
```

### Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Language** | Python 3.11+ | Core development |
| **Package Manager** | uv | Fast dependency management |
| **Speech-to-Text** | IBM Watson STT | Audio transcription |
| **Language Model** | IBM watsonx.ai (default) | Intelligent responses |
| **Alternative LLMs** | OpenAI, Claude, Ollama | Multi-provider support |
| **Text-to-Speech** | Edge TTS / IBM Watson | Voice synthesis |
| **UI Framework** | PySide6 (Qt6) | Desktop interface |
| **Audio Processing** | sounddevice, webrtcvad | Audio I/O & VAD |
| **Configuration** | Pydantic | Settings validation |

---

## 🔌 API Integration

### IBM Watson Speech-to-Text

```python
from meeting_copilot.stt import WatsonSTT

stt = WatsonSTT(
    api_key="your_api_key",
    url="your_service_url"
)

transcript, confidence = stt.transcribe_pcm16(audio_bytes, 16000)
```

### IBM watsonx.ai LLM (Default)

```python
from meeting_copilot.llm import LLMClient
from meeting_copilot.config import LLMProvider

# Uses watsonx.ai by default from .env configuration
llm = LLMClient()

response = llm.respond(
    mode="answer",
    transcript_context="Meeting discussion..."
)
```

### Multi-Provider LLM Support

```python
from meeting_copilot.llm import LLMClient
from meeting_copilot.config import LLMProvider

# Explicitly specify provider
llm_watsonx = LLMClient(provider=LLMProvider.watsonx)
llm_openai = LLMClient(provider=LLMProvider.openai)
llm_claude = LLMClient(provider=LLMProvider.claude)
llm_ollama = LLMClient(provider=LLMProvider.ollama)

# List available models
from meeting_copilot.llm.model_catalog import list_models_for_provider

models, error = list_models_for_provider(LLMProvider.watsonx)
if not error:
    print(f"Available watsonx.ai models: {models}")
```

### Edge TTS

```python
from meeting_copilot.tts import EdgeTTSClient

tts = EdgeTTSClient(voice="en-US-GuyNeural")
tts.speak("Hello, this is Watson")
```

---

## 🛠️ Development

### Available Make Commands

```bash
make help        # 📖 Show all available commands
make install     # 📦 Install dependencies with uv
make run         # ▶️  Run desktop application
make console     # 🖥️ Run console mode (no UI)
make dev         # 🔧 Run development mode
make test        # ✅ Run test suite
make lint        # 🔍 Run code linting
make format      # ✨ Auto-format code
make clean       # 🧹 Clean generated files
make update      # ⬆️  Update dependencies
make build       # 📦 Build distribution package
```

### Project Setup for Development

```bash
# Clone repository
git clone https://github.com/ruslanmv/Virtual-Webcam-Chatbot.git
cd Virtual-Webcam-Chatbot

# Install development dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Check code quality
make lint
```

### Code Quality Standards

- ✅ **PEP 8** compliance
- ✅ **Type hints** throughout
- ✅ **100 character** line limit
- ✅ **Comprehensive** docstrings
- ✅ **Unit tests** for critical paths

### Running Tests

```bash
# All tests
make test

# Specific module
uv run pytest tests/test_audio.py

# With coverage report
uv run pytest --cov=meeting_copilot --cov-report=html
```

---

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>❌ "No loopback device found"</b></summary>

**Windows:**
1. Open Sound Settings
2. Navigate to "Recording" tab
3. Right-click → Show Disabled Devices
4. Enable "Stereo Mix"
5. Set as default recording device
6. Restart application

**Linux/macOS:**
System audio capture requires additional setup. Use microphone mode or install virtual audio cable.

</details>

<details>
<summary><b>❌ "Watson STT connection failed"</b></summary>

**Solution:**
1. Verify API key in `.env` file
2. Check service URL format
3. Test credentials at [IBM Cloud Console](https://cloud.ibm.com)
4. Ensure internet connection
5. Check firewall settings

</details>

<details>
<summary><b>❌ "LLM API error"</b></summary>

**For watsonx.ai (default):**
1. Verify `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` in `.env`
2. Check credentials at [IBM Cloud Console](https://cloud.ibm.com)
3. Ensure project ID is correct
4. Try different model: `WATSONX_MODEL_ID=ibm/granite-3-8b-instruct`

**For OpenAI:**
1. Verify `OPENAI_API_KEY` in `.env`
2. Check API key has credits
3. Visit [OpenAI Platform](https://platform.openai.com) to verify status
4. Try different model: `OPENAI_MODEL=gpt-3.5-turbo`

**For Claude:**
1. Verify `ANTHROPIC_API_KEY` in `.env`
2. Check usage limits at [Anthropic Console](https://console.anthropic.com/)

</details>

<details>
<summary><b>⚠️ "High latency / slow responses"</b></summary>

**Optimizations:**
1. Use Edge TTS: `TTS_PROVIDER=edge`
2. Reduce buffer: `PREWAKE_BUFFER_SECONDS=10`
3. Use faster model:
   - watsonx.ai: `WATSONX_MODEL_ID=ibm/granite-3-8b-instruct`
   - OpenAI: `OPENAI_MODEL=gpt-3.5-turbo`
   - Ollama: `OLLAMA_MODEL=llama3` (local, fastest)
4. Increase VAD aggressiveness: `VAD_AGGRESSIVENESS=3`

</details>

<details>
<summary><b>⚠️ "Poor audio quality / false triggers"</b></summary>

**Solutions:**
1. Adjust VAD: `VAD_AGGRESSIVENESS=1` (less aggressive)
2. Increase padding: `VAD_PADDING_MS=500`
3. Use better microphone
4. Reduce background noise
5. Check sample rate: `SAMPLE_RATE=16000`

</details>

### Getting Help

- 📖 **Documentation**: See [README_COPILOT.md](README_COPILOT.md)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/ruslanmv/Virtual-Webcam-Chatbot/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ruslanmv/Virtual-Webcam-Chatbot/discussions)
- 📧 **Email**: contact@ruslanmv.com

---

## 🗺️ Roadmap

### v1.0 (Current - Production Ready) ✅

- ✅ Wake word detection (text-based)
- ✅ Multi-source audio capture
- ✅ Real-time transcription (IBM Watson STT)
- ✅ Multi-provider LLM (watsonx.ai, OpenAI, Claude, Ollama)
- ✅ Model catalog for provider discovery
- ✅ Text-to-speech output
- ✅ Desktop UI (PySide6)
- ✅ Privacy controls

### v1.1 (Q1 2025) 🚧

- 🔲 Real keyword spotting (Porcupine/Whisper)
- 🔲 Virtual webcam overlay
- 🔲 Zoom/Teams native integration
- 🔲 Custom wake word training
- 🔲 Multi-language support (ES, FR, DE)
- 🔲 Meeting analytics dashboard

### v1.2 (Q2 2025) 📋

- 🔲 Offline mode with local models
- 🔲 Action item extraction
- 🔲 Calendar integration
- 🔲 Export meeting transcripts
- 🔲 macOS native support
- 🔲 Linux support enhancements

### v2.0 (Q3 2025) 🎯

- 🔲 Mobile companion app
- 🔲 Cloud sync
- 🔲 Team collaboration features
- 🔲 Advanced analytics
- 🔲 Plugin ecosystem
- 🔲 Enterprise SSO

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute

- 🐛 **Report Bugs** - Help us identify issues
- 💡 **Suggest Features** - Share your ideas
- 📝 **Improve Documentation** - Make it clearer
- 🔧 **Submit Pull Requests** - Contribute code
- ⭐ **Star the Project** - Show your support

### Development Process

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

```
Copyright 2025 Ruslan Magana

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## 👨‍💻 Contact

<div align="center">

**Ruslan Magana**

[![Email](https://img.shields.io/badge/Email-contact@ruslanmv.com-red?logo=gmail&logoColor=white)](mailto:contact@ruslanmv.com)
[![Website](https://img.shields.io/badge/Website-ruslanmv.com-blue?logo=google-chrome&logoColor=white)](https://ruslanmv.com)
[![GitHub](https://img.shields.io/badge/GitHub-ruslanmv-black?logo=github&logoColor=white)](https://github.com/ruslanmv)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Ruslan_Magana-0077B5?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ruslanmv/)

</div>

---

## 🙏 Acknowledgments

Special thanks to:

- **IBM watsonx.ai** - Enterprise-grade foundation models
- **IBM Watson** - World-class speech services (STT & TTS)
- **OpenAI** - Advanced language model alternatives
- **Anthropic** - Claude AI capabilities
- **Microsoft Edge** - Free TTS service
- **WebRTC Project** - VAD technology
- **Qt Project** - Cross-platform UI framework
- **Python Community** - Amazing ecosystem

<div align="center">

### 🎉 Built with ❤️ for Better Meetings

**Make your meetings more productive with AI**

[⬆ Back to Top](#-meeting-copilot)

</div>
