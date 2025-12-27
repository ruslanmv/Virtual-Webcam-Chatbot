# Contributing to Meeting Copilot

Thank you for your interest in contributing to Meeting Copilot! This document provides guidelines and instructions for contributing to the project.

## 🤝 Code of Conduct

- Be respectful and constructive
- Focus on improving the project
- Help create a welcoming environment for all contributors

## 🐛 Reporting Bugs

Before submitting a bug report:

1. Check existing issues to avoid duplicates
2. Test with the latest version
3. Verify your configuration (.env file)

When reporting bugs, include:

- **Description**: Clear description of the issue
- **Steps to reproduce**: Detailed steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, etc.
- **Logs**: Relevant error messages or logs

## 💡 Suggesting Features

We welcome feature suggestions! Please:

1. Check existing feature requests
2. Describe the use case clearly
3. Explain how it benefits users
4. Consider implementation complexity

## 🔧 Development Setup

### Prerequisites

- Python 3.11+
- uv package manager
- Git

### Setup Steps

1. **Fork and clone**

```bash
git clone https://github.com/YOUR_USERNAME/Virtual-Webcam-Chatbot.git
cd Virtual-Webcam-Chatbot
```

2. **Install dependencies**

```bash
make install-dev
```

3. **Configure environment**

```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run tests**

```bash
make test
```

## 📝 Coding Standards

### Style Guide

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use descriptive variable names

### Code Quality

Run before committing:

```bash
make format    # Auto-format code
make lint      # Check code quality
make test      # Run tests
```

### Documentation

- Add docstrings to all functions/classes
- Update README for user-facing changes
- Include inline comments for complex logic

## 🔀 Pull Request Process

### Before Submitting

1. **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new features
   - Update documentation

3. **Test thoroughly**

```bash
make test
make lint
```

4. **Commit with clear messages**

```bash
git commit -m "feat: Add new feature description"
```

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Formatting changes
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance tasks

### Submitting

1. **Push to your fork**

```bash
git push origin feature/your-feature-name
```

2. **Create Pull Request**
   - Use a clear, descriptive title
   - Reference related issues
   - Describe changes and rationale
   - Include screenshots for UI changes

3. **Code Review**
   - Address review comments
   - Keep discussion professional
   - Be open to feedback

## 🧪 Testing

### Running Tests

```bash
# All tests
make test

# Specific module
uv run pytest tests/test_audio.py

# With coverage
uv run pytest --cov=meeting_copilot
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names
- Test edge cases

Example:

```python
def test_vad_detects_speech():
    """Test that VAD correctly detects speech segments"""
    vad = VADSegmenter(sample_rate=16000)
    # ... test implementation
```

## 📁 Project Structure

```
meeting_copilot/
├── src/meeting_copilot/    # Main package
│   ├── audio/              # Audio processing
│   ├── stt/                # Speech-to-text
│   ├── wakeword/           # Wake word detection
│   ├── llm/                # Language model
│   ├── tts/                # Text-to-speech
│   ├── ui/                 # User interface
│   ├── config.py           # Configuration
│   └── app.py              # Main application
├── tests/                  # Test suite
├── docs/                   # Documentation
└── pyproject.toml          # Project metadata
```

## 🎯 Areas to Contribute

### High Priority

- [ ] Cross-platform support (macOS, Linux)
- [ ] Real keyword spotting (not text-based)
- [ ] Performance optimizations
- [ ] Additional tests

### Medium Priority

- [ ] Virtual webcam overlay
- [ ] Meeting platform integrations
- [ ] Multi-language support
- [ ] Custom wake words

### Low Priority

- [ ] UI themes
- [ ] Advanced analytics
- [ ] Plugin system

## 💬 Getting Help

- **Issues**: [GitHub Issues](https://github.com/ruslanmv/Virtual-Webcam-Chatbot/issues)
- **Email**: contact@ruslanmv.com
- **Documentation**: See README_COPILOT.md

## 📜 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

**Thank you for contributing to Meeting Copilot!** 🎉

Developed by Ruslan Magana (contact@ruslanmv.com)
