"""
Model catalog for listing available LLM models from each provider

Allows users to discover models from watsonx.ai, OpenAI, Claude, and Ollama.
Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

import os
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

import requests

from meeting_copilot.config import LLMProvider, get_secrets, get_settings


# ============================================================================
# Watsonx.ai Configuration (public endpoint, no key needed for listing)
# ============================================================================

WATSONX_BASE_URLS = [
    "https://us-south.ml.cloud.ibm.com",
    "https://eu-de.ml.cloud.ibm.com",
    "https://jp-tok.ml.cloud.ibm.com",
    "https://au-syd.ml.cloud.ibm.com",
]

WATSONX_ENDPOINT = "/ml/v1/foundation_model_specs"
WATSONX_PARAMS = {
    "version": "2024-09-16",
    "filters": "!function_embedding,!lifecycle_withdrawn",
}
TODAY = datetime.today().strftime("%Y-%m-%d")


def _is_deprecated_or_withdrawn(lifecycle: List[Dict[str, Any]]) -> bool:
    """
    Check if a model is deprecated or withdrawn.

    Args:
        lifecycle: List of lifecycle entries from watsonx.ai API

    Returns:
        True if model is deprecated/withdrawn and active today
    """
    for entry in lifecycle:
        if entry.get("id") in {"deprecated", "withdrawn"}:
            if entry.get("start_date", "") <= TODAY:
                return True
    return False


# ============================================================================
# Provider-specific listing functions
# ============================================================================


def _list_watsonx_models() -> Tuple[List[str], Optional[str]]:
    """
    List foundation models from watsonx.ai public specs endpoint.

    No API key required for IBM-managed models listing.
    Returns unique sorted list of model IDs across major regions.

    Returns:
        tuple: (model_list, error_message)
    """
    all_models = set()

    for base in WATSONX_BASE_URLS:
        url = f"{base}{WATSONX_ENDPOINT}"
        try:
            resp = requests.get(url, params=WATSONX_PARAMS, timeout=10)
            resp.raise_for_status()
            resources = resp.json().get("resources", [])

            for model in resources:
                # Skip deprecated/withdrawn models
                if _is_deprecated_or_withdrawn(model.get("lifecycle", [])):
                    continue

                model_id = model.get("model_id")
                if model_id:
                    all_models.add(model_id)

        except Exception as e:
            # Skip this region on error, try others
            print(f"Warning: Failed to fetch from {base}: {e}")
            continue

    if not all_models:
        return [], "No watsonx.ai models found (API call failed for all regions)"

    return sorted(all_models), None


def _list_openai_models() -> Tuple[List[str], Optional[str]]:
    """
    List models from OpenAI /v1/models endpoint.

    Requires OPENAI_API_KEY to be configured.

    Returns:
        tuple: (model_list, error_message)
    """
    secrets = get_secrets()
    api_key = secrets.openai_api_key or os.getenv("OPENAI_API_KEY")

    if not api_key:
        return [], "OpenAI API key not configured (OPENAI_API_KEY)"

    base_url = secrets.openai_base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
    url = f"{base_url.rstrip('/')}/v1/models"

    try:
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        resp.raise_for_status()

        data = resp.json().get("data", [])
        models = sorted({m.get("id", "") for m in data if m.get("id")})

        return models, None

    except Exception as e:
        return [], f"Error listing OpenAI models: {e}"


def _list_claude_models() -> Tuple[List[str], Optional[str]]:
    """
    List models from Anthropic /v1/models endpoint.

    Requires ANTHROPIC_API_KEY to be configured.

    Returns:
        tuple: (model_list, error_message)
    """
    secrets = get_secrets()
    api_key = secrets.claude_api_key or os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return [], "Anthropic API key not configured (ANTHROPIC_API_KEY)"

    base_url = secrets.claude_base_url or os.getenv(
        "ANTHROPIC_BASE_URL",
        "https://api.anthropic.com"
    )
    url = f"{base_url.rstrip('/')}/v1/models"
    anthropic_version = os.getenv("ANTHROPIC_VERSION", "2023-06-01")

    try:
        resp = requests.get(
            url,
            headers={
                "x-api-key": api_key,
                "anthropic-version": anthropic_version,
            },
            timeout=10,
        )
        resp.raise_for_status()

        data = resp.json().get("data", [])
        models = sorted({m.get("id", "") for m in data if m.get("id")})

        return models, None

    except Exception as e:
        return [], f"Error listing Claude models: {e}"


def _list_ollama_models() -> Tuple[List[str], Optional[str]]:
    """
    List models from local/remote Ollama server via /api/tags.

    Uses OLLAMA_BASE_URL from config or environment.

    Returns:
        tuple: (model_list, error_message)
    """
    secrets = get_secrets()
    base_url = secrets.ollama_base_url or os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )
    url = f"{base_url.rstrip('/')}/api/tags"

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()

        data = resp.json().get("models", [])
        models = sorted({m.get("name", "") for m in data if m.get("name")})

        return models, None

    except Exception as e:
        return [], f"Error listing Ollama models from {url}: {e}"


# ============================================================================
# Public API
# ============================================================================


def list_models_for_provider(
    provider: LLMProvider,
) -> Tuple[List[str], Optional[str]]:
    """
    List available models for a given LLM provider.

    Args:
        provider: LLM provider enum (watsonx, openai, claude, ollama)

    Returns:
        tuple: (models, error)
            - models: List of model IDs/names (empty if error)
            - error: Human-readable error message (None if successful)

    Example:
        >>> models, error = list_models_for_provider(LLMProvider.watsonx)
        >>> if error:
        ...     print(f"Error: {error}")
        ... else:
        ...     for model in models:
        ...         print(model)
    """
    if provider == LLMProvider.watsonx:
        return _list_watsonx_models()
    elif provider == LLMProvider.openai:
        return _list_openai_models()
    elif provider == LLMProvider.claude:
        return _list_claude_models()
    elif provider == LLMProvider.ollama:
        return _list_ollama_models()
    else:
        return [], f"Unsupported provider: {provider}"


def list_all_models() -> Dict[str, Tuple[List[str], Optional[str]]]:
    """
    List models from all configured providers.

    Returns:
        dict: Provider name -> (models, error) mapping

    Example:
        >>> results = list_all_models()
        >>> for provider_name, (models, error) in results.items():
        ...     if error:
        ...         print(f"{provider_name}: {error}")
        ...     else:
        ...         print(f"{provider_name}: {len(models)} models")
    """
    results = {}

    for provider in LLMProvider:
        results[provider.value] = list_models_for_provider(provider)

    return results


def get_recommended_models(provider: LLMProvider) -> List[str]:
    """
    Get recommended models for a provider (curated list).

    Args:
        provider: LLM provider enum

    Returns:
        List of recommended model IDs
    """
    recommendations = {
        LLMProvider.watsonx: [
            "meta-llama/llama-3-3-70b-instruct",
            "meta-llama/llama-3-1-70b-instruct",
            "ibm/granite-3-8b-instruct",
            "ibm/granite-3.1-8b-instruct",
            "mistralai/mistral-large",
        ],
        LLMProvider.openai: [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ],
        LLMProvider.claude: [
            "claude-opus-4-5",
            "claude-sonnet-4-5",
            "claude-sonnet-3-7",
            "claude-3-5-sonnet-20241022",
        ],
        LLMProvider.ollama: [
            "llama3",
            "llama3.1",
            "mistral",
            "mixtral",
            "codellama",
        ],
    }

    return recommendations.get(provider, [])


def print_models_for_provider(provider: LLMProvider) -> None:
    """
    Print available models for a provider (for CLI usage).

    Args:
        provider: LLM provider enum
    """
    print(f"\n{'=' * 60}")
    print(f"Available models for {provider.value.upper()}")
    print(f"{'=' * 60}\n")

    models, error = list_models_for_provider(provider)

    if error:
        print(f"❌ Error: {error}\n")
        return

    if not models:
        print("No models found.\n")
        return

    print(f"Found {len(models)} models:\n")

    # Get recommended models for highlighting
    recommended = get_recommended_models(provider)

    for model in models:
        marker = "⭐" if model in recommended else "  "
        print(f"{marker} {model}")

    print(f"\n⭐ = Recommended for Meeting Copilot")
    print(f"{'=' * 60}\n")


def print_all_models() -> None:
    """Print available models from all providers (for CLI usage)."""
    results = list_all_models()

    for provider_name, (models, error) in results.items():
        provider = LLMProvider(provider_name)
        print_models_for_provider(provider)


# ============================================================================
# CLI Interface (for testing)
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        provider_name = sys.argv[1].lower()
        try:
            provider = LLMProvider(provider_name)
            print_models_for_provider(provider)
        except ValueError:
            print(f"Unknown provider: {provider_name}")
            print(f"Valid options: {', '.join(p.value for p in LLMProvider)}")
    else:
        print_all_models()
