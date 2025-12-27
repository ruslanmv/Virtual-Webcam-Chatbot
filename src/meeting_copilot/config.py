"""
Configuration management for Meeting Copilot

Multi-provider LLM support with watsonx.ai as default provider.
Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

import enum
import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, enum.Enum):
    """Supported LLM providers"""
    watsonx = "watsonx"  # IBM watsonx.ai (default - we love IBM!)
    openai = "openai"    # OpenAI GPT models
    claude = "claude"    # Anthropic Claude
    ollama = "ollama"    # Local Ollama models


class AppSettings(BaseSettings):
    """Application settings loaded from environment variables and .env file"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application metadata
    app_name: str = Field(default="Meeting Copilot", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    developer: str = Field(
        default="Ruslan Magana", description="Developer name"
    )
    contact: str = Field(
        default="contact@ruslanmv.com", description="Developer contact"
    )

    # Bot configuration
    bot_name: str = Field(
        default="watson",
        description="Wake word / bot name (case-insensitive)",
    )

    # Audio settings
    sample_rate: int = Field(
        default=16000,
        description="Audio sample rate in Hz (16000 recommended for STT)",
    )
    channels: int = Field(default=1, description="Number of audio channels (mono)")
    chunk_size: int = Field(
        default=480,
        description="Audio chunk size in frames (30ms at 16kHz)",
    )

    # VAD (Voice Activity Detection) settings
    vad_aggressiveness: int = Field(
        default=2,
        ge=0,
        le=3,
        description="VAD aggressiveness (0=least, 3=most aggressive)",
    )
    vad_frame_ms: int = Field(
        default=30,
        description="VAD frame duration in ms (10, 20, or 30)",
    )
    vad_padding_ms: int = Field(
        default=300,
        description="Silence padding in ms before/after speech",
    )

    # Buffer settings
    prewake_buffer_seconds: int = Field(
        default=20,
        description="Seconds of audio to keep before wake word",
    )
    max_utterance_seconds: int = Field(
        default=30,
        description="Maximum utterance length in seconds",
    )

    # Audio input source
    audio_source: Literal["microphone", "system", "both"] = Field(
        default="microphone",
        description="Audio input source",
    )

    # Assistant modes
    default_mode: Literal["answer", "opinion", "summarize"] = Field(
        default="answer",
        description="Default assistant mode",
    )

    # Privacy settings
    enable_logging: bool = Field(
        default=False,
        description="Enable conversation logging (opt-in)",
    )
    log_directory: Path = Field(
        default=Path("logs"),
        description="Directory for conversation logs",
    )
    encrypt_logs: bool = Field(
        default=True,
        description="Encrypt conversation logs",
    )

    # UI settings
    show_transcript: bool = Field(
        default=True,
        description="Show real-time transcript",
    )
    show_confidence: bool = Field(
        default=False,
        description="Show STT confidence scores",
    )
    enable_tray_icon: bool = Field(
        default=True,
        description="Enable system tray icon",
    )

    # Performance settings
    latency_target_ms: int = Field(
        default=2500,
        description="Target latency from wake to response (ms)",
    )

    # Development settings
    debug: bool = Field(default=False, description="Enable debug mode")
    console_mode: bool = Field(
        default=False,
        description="Run in console mode (no UI)",
    )


class Secrets(BaseSettings):
    """API keys and secrets loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ============================================================================
    # LLM Provider Selection (watsonx.ai is default - we love IBM!)
    # ============================================================================
    llm_provider: LLMProvider = Field(
        default=LLMProvider.watsonx,
        description="LLM provider to use (watsonx, openai, claude, ollama)",
    )

    # ============================================================================
    # IBM watsonx.ai (DEFAULT PROVIDER)
    # ============================================================================
    watsonx_api_key: str = Field(
        default="",
        description="IBM watsonx.ai API key",
    )
    watsonx_project_id: str = Field(
        default="",
        description="IBM watsonx.ai project ID",
    )
    watsonx_model_id: str = Field(
        default="meta-llama/llama-3-3-70b-instruct",
        description="IBM watsonx.ai model ID",
    )
    watsonx_base_url: str = Field(
        default="https://us-south.ml.cloud.ibm.com",
        description="IBM watsonx.ai base URL",
    )
    watsonx_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="IBM watsonx.ai temperature",
    )
    watsonx_max_tokens: int = Field(
        default=1024,
        description="IBM watsonx.ai max tokens",
    )

    # ============================================================================
    # IBM Watson Speech-to-Text
    # ============================================================================
    ibm_stt_api_key: str = Field(
        default="",
        alias="IBM_SPEECH_TO_TEXT_API",
        description="IBM Watson STT API key",
    )
    ibm_stt_url: str = Field(
        default="",
        alias="IBM_STT_URL",
        description="IBM Watson STT service URL",
    )
    ibm_stt_model: str = Field(
        default="en-US_BroadbandModel",
        description="IBM Watson STT model",
    )

    # ============================================================================
    # IBM Watson Text-to-Speech (optional)
    # ============================================================================
    ibm_tts_api_key: str = Field(
        default="",
        alias="IBM_TTS_API_KEY",
        description="IBM Watson TTS API key",
    )
    ibm_tts_url: str = Field(
        default="",
        alias="IBM_TTS_URL",
        description="IBM Watson TTS service URL",
    )
    ibm_tts_voice: str = Field(
        default="en-US_AllisonV3Voice",
        description="IBM Watson TTS voice",
    )

    # ============================================================================
    # OpenAI (Alternative LLM Provider)
    # ============================================================================
    openai_api_key: str = Field(
        default="",
        alias="OPENAI_API_KEY",
        description="OpenAI API key",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use",
    )
    openai_base_url: str = Field(
        default="",
        description="OpenAI base URL (for Azure or proxies)",
    )
    openai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="OpenAI temperature",
    )

    # ============================================================================
    # Anthropic Claude (Alternative LLM Provider)
    # ============================================================================
    claude_api_key: str = Field(
        default="",
        alias="ANTHROPIC_API_KEY",
        description="Anthropic Claude API key",
    )
    claude_model: str = Field(
        default="claude-sonnet-4-5",
        description="Claude model to use",
    )
    claude_base_url: str = Field(
        default="",
        description="Claude base URL (for proxies)",
    )
    claude_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Claude temperature",
    )

    # ============================================================================
    # Ollama (Local LLM Provider)
    # ============================================================================
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama base URL",
    )
    ollama_model: str = Field(
        default="llama3",
        description="Ollama model to use",
    )

    # ============================================================================
    # TTS Provider Selection
    # ============================================================================
    tts_provider: Literal["ibm", "edge"] = Field(
        default="edge",
        description="TTS provider (ibm or edge)",
    )
    edge_tts_voice: str = Field(
        default="en-US-GuyNeural",
        description="Edge TTS voice",
    )


# Global settings instance
_settings: Optional[AppSettings] = None
_secrets: Optional[Secrets] = None


def get_settings() -> AppSettings:
    """Get application settings (singleton)"""
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings


def get_secrets() -> Secrets:
    """Get API secrets (singleton)"""
    global _secrets
    if _secrets is None:
        _secrets = Secrets()
    return _secrets


def validate_configuration() -> tuple[bool, list[str]]:
    """
    Validate that required configuration is present

    Returns:
        tuple: (is_valid, list of error messages)
    """
    errors = []
    secrets = get_secrets()

    # Check required API keys for STT
    if not secrets.ibm_stt_api_key or not secrets.ibm_stt_url:
        errors.append(
            "Missing IBM Watson STT credentials (IBM_SPEECH_TO_TEXT_API, IBM_STT_URL)"
        )

    # Check required API keys based on selected LLM provider
    provider = secrets.llm_provider

    if provider == LLMProvider.watsonx:
        if not secrets.watsonx_api_key:
            errors.append("Missing IBM watsonx.ai API key (WATSONX_API_KEY)")
        if not secrets.watsonx_project_id:
            errors.append("Missing IBM watsonx.ai project ID (WATSONX_PROJECT_ID)")

    elif provider == LLMProvider.openai:
        if not secrets.openai_api_key:
            errors.append("Missing OpenAI API key (OPENAI_API_KEY)")

    elif provider == LLMProvider.claude:
        if not secrets.claude_api_key:
            errors.append("Missing Anthropic Claude API key (ANTHROPIC_API_KEY)")

    elif provider == LLMProvider.ollama:
        if not secrets.ollama_base_url:
            errors.append("Missing Ollama base URL (OLLAMA_BASE_URL)")

    # Check TTS configuration
    if secrets.tts_provider == "ibm":
        if not secrets.ibm_tts_api_key or not secrets.ibm_tts_url:
            errors.append(
                "IBM TTS selected but credentials missing (IBM_TTS_API_KEY, IBM_TTS_URL)"
            )

    return len(errors) == 0, errors


def load_config() -> tuple[AppSettings, Secrets]:
    """
    Load and validate configuration

    Returns:
        tuple: (settings, secrets)

    Raises:
        ValueError: If required configuration is missing
    """
    settings = get_settings()
    secrets = get_secrets()

    is_valid, errors = validate_configuration()
    if not is_valid:
        error_msg = "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)

    return settings, secrets
