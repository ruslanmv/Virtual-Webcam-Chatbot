"""
Multi-provider LLM client for generating responses

Supports: IBM watsonx.ai (default), OpenAI, Anthropic Claude, and Ollama
Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

import os
from typing import Iterator, Literal, Optional

from meeting_copilot.config import LLMProvider, get_secrets

from .prompts import build_messages


class LLMClient:
    """
    Multi-provider LLM client for generating assistant responses.

    Supports:
    - IBM watsonx.ai (default - we love IBM!)
    - OpenAI GPT models
    - Anthropic Claude
    - Local Ollama models
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        """
        Initialize LLM client

        Args:
            provider: LLM provider to use (None = use config default)
        """
        secrets = get_secrets()

        # Use provided provider or default from config
        self.provider = provider or secrets.llm_provider

        # Initialize provider-specific client
        if self.provider == LLMProvider.watsonx:
            self._init_watsonx(secrets)
        elif self.provider == LLMProvider.openai:
            self._init_openai(secrets)
        elif self.provider == LLMProvider.claude:
            self._init_claude(secrets)
        elif self.provider == LLMProvider.ollama:
            self._init_ollama(secrets)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _init_watsonx(self, secrets):
        """Initialize IBM watsonx.ai client"""
        try:
            from ibm_watsonx_ai import APIClient
            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference
        except ImportError:
            raise ImportError(
                "IBM watsonx.ai SDK not installed. "
                "Install with: pip install ibm-watsonx-ai"
            )

        if not secrets.watsonx_api_key:
            raise ValueError("Missing watsonx.ai API key (WATSONX_API_KEY)")
        if not secrets.watsonx_project_id:
            raise ValueError("Missing watsonx.ai project ID (WATSONX_PROJECT_ID)")

        # Set environment variables for SDK
        os.environ["WATSONX_API_KEY"] = secrets.watsonx_api_key
        os.environ["WATSONX_PROJECT_ID"] = secrets.watsonx_project_id
        os.environ["WATSONX_URL"] = secrets.watsonx_base_url

        # Create credentials and client
        credentials = Credentials(
            api_key=secrets.watsonx_api_key,
            url=secrets.watsonx_base_url,
        )

        self.client = APIClient(credentials=credentials)

        # Model configuration
        self.model_id = secrets.watsonx_model_id
        self.project_id = secrets.watsonx_project_id
        self.temperature = secrets.watsonx_temperature
        self.max_tokens = secrets.watsonx_max_tokens

        print(f"✅ IBM watsonx.ai initialized (model: {self.model_id})")

    def _init_openai(self, secrets):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed. "
                "Install with: pip install openai"
            )

        if not secrets.openai_api_key:
            raise ValueError("Missing OpenAI API key (OPENAI_API_KEY)")

        self.client = OpenAI(
            api_key=secrets.openai_api_key,
            base_url=secrets.openai_base_url if secrets.openai_base_url else None,
        )

        self.model = secrets.openai_model
        self.temperature = secrets.openai_temperature

        print(f"✅ OpenAI initialized (model: {self.model})")

    def _init_claude(self, secrets):
        """Initialize Anthropic Claude client"""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "Anthropic SDK not installed. "
                "Install with: pip install anthropic"
            )

        if not secrets.claude_api_key:
            raise ValueError("Missing Claude API key (ANTHROPIC_API_KEY)")

        # Set environment variable (required by SDK)
        os.environ["ANTHROPIC_API_KEY"] = secrets.claude_api_key

        self.client = Anthropic(
            api_key=secrets.claude_api_key,
            base_url=secrets.claude_base_url if secrets.claude_base_url else None,
        )

        self.model = secrets.claude_model
        self.temperature = secrets.claude_temperature

        print(f"✅ Anthropic Claude initialized (model: {self.model})")

    def _init_ollama(self, secrets):
        """Initialize Ollama client"""
        try:
            from openai import OpenAI  # Ollama uses OpenAI-compatible API
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed (needed for Ollama). "
                "Install with: pip install openai"
            )

        if not secrets.ollama_base_url:
            raise ValueError("Missing Ollama base URL (OLLAMA_BASE_URL)")

        self.client = OpenAI(
            base_url=secrets.ollama_base_url + "/v1",
            api_key="ollama",  # Ollama doesn't need a real API key
        )

        self.model = secrets.ollama_model
        self.temperature = 0.7

        print(f"✅ Ollama initialized (model: {self.model}, url: {secrets.ollama_base_url})")

    def respond(
        self,
        mode: Literal["answer", "opinion", "summarize"],
        transcript_context: str,
        custom_instruction: str = "",
        max_tokens: int = 500,
    ) -> str:
        """
        Generate response based on conversation context

        Args:
            mode: Response mode (answer/opinion/summarize)
            transcript_context: Recent conversation transcript
            custom_instruction: Optional custom instruction
            max_tokens: Maximum response tokens

        Returns:
            Generated response text
        """
        # Build messages
        messages = build_messages(mode, transcript_context, custom_instruction)

        try:
            if self.provider == LLMProvider.watsonx:
                return self._respond_watsonx(messages, max_tokens)
            elif self.provider == LLMProvider.openai:
                return self._respond_openai(messages, max_tokens)
            elif self.provider == LLMProvider.claude:
                return self._respond_claude(messages, max_tokens)
            elif self.provider == LLMProvider.ollama:
                return self._respond_ollama(messages, max_tokens)
            else:
                return "I'm sorry, I'm having trouble generating a response right now."

        except Exception as e:
            print(f"LLM error ({self.provider}): {e}")
            return "I'm sorry, I'm having trouble generating a response right now."

    def _respond_watsonx(self, messages: list[dict], max_tokens: int) -> str:
        """Generate response using IBM watsonx.ai"""
        from ibm_watsonx_ai.foundation_models import ModelInference

        # Create model inference
        model = ModelInference(
            model_id=self.model_id,
            api_client=self.client,
            project_id=self.project_id,
            params={
                "temperature": self.temperature,
                "max_new_tokens": max_tokens,
            },
        )

        # Convert messages to prompt (watsonx.ai uses text prompts)
        prompt = self._messages_to_prompt(messages)

        # Generate response
        response = model.generate_text(prompt=prompt)

        return response.strip()

    def _respond_openai(self, messages: list[dict], max_tokens: int) -> str:
        """Generate response using OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=max_tokens,
            n=1,
        )

        return response.choices[0].message.content.strip()

    def _respond_claude(self, messages: list[dict], max_tokens: int) -> str:
        """Generate response using Anthropic Claude"""
        # Extract system message and user messages
        system_msg = ""
        user_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)

        response = self.client.messages.create(
            model=self.model,
            system=system_msg,
            messages=user_messages,
            temperature=self.temperature,
            max_tokens=max_tokens,
        )

        return response.content[0].text.strip()

    def _respond_ollama(self, messages: list[dict], max_tokens: int) -> str:
        """Generate response using Ollama"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content.strip()

    def _messages_to_prompt(self, messages: list[dict]) -> str:
        """Convert OpenAI-style messages to text prompt for watsonx.ai"""
        prompt_parts = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)

    def respond_streaming(
        self,
        mode: Literal["answer", "opinion", "summarize"],
        transcript_context: str,
        custom_instruction: str = "",
        max_tokens: int = 500,
    ) -> Iterator[str]:
        """
        Generate streaming response (if supported by provider)

        Args:
            mode: Response mode
            transcript_context: Recent conversation transcript
            custom_instruction: Optional custom instruction
            max_tokens: Maximum response tokens

        Yields:
            Response text chunks
        """
        messages = build_messages(mode, transcript_context, custom_instruction)

        try:
            if self.provider == LLMProvider.openai:
                yield from self._stream_openai(messages, max_tokens)
            elif self.provider == LLMProvider.claude:
                yield from self._stream_claude(messages, max_tokens)
            elif self.provider == LLMProvider.ollama:
                yield from self._stream_ollama(messages, max_tokens)
            else:
                # Fallback to non-streaming for providers that don't support it
                yield self.respond(mode, transcript_context, custom_instruction, max_tokens)

        except Exception as e:
            print(f"LLM streaming error ({self.provider}): {e}")
            yield "I'm sorry, I'm having trouble generating a response right now."

    def _stream_openai(self, messages: list[dict], max_tokens: int) -> Iterator[str]:
        """Stream response from OpenAI"""
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def _stream_claude(self, messages: list[dict], max_tokens: int) -> Iterator[str]:
        """Stream response from Claude"""
        # Extract system message
        system_msg = ""
        user_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)

        with self.client.messages.stream(
            model=self.model,
            system=system_msg,
            messages=user_messages,
            temperature=self.temperature,
            max_tokens=max_tokens,
        ) as stream:
            for text in stream.text_stream:
                yield text

    def _stream_ollama(self, messages: list[dict], max_tokens: int) -> Iterator[str]:
        """Stream response from Ollama"""
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def quick_response(
        self,
        prompt: str,
        max_tokens: int = 200,
    ) -> str:
        """
        Generate quick response to a simple prompt

        Args:
            prompt: User prompt
            max_tokens: Maximum response tokens

        Returns:
            Generated response
        """
        messages = [{"role": "user", "content": prompt}]

        try:
            if self.provider == LLMProvider.watsonx:
                return self._respond_watsonx(messages, max_tokens)
            elif self.provider == LLMProvider.openai:
                return self._respond_openai(messages, max_tokens)
            elif self.provider == LLMProvider.claude:
                return self._respond_claude(messages, max_tokens)
            elif self.provider == LLMProvider.ollama:
                return self._respond_ollama(messages, max_tokens)
            else:
                return "Error generating response."

        except Exception as e:
            print(f"LLM quick response error ({self.provider}): {e}")
            return "Error generating response."

    def test_connection(self) -> bool:
        """
        Test LLM connection

        Returns:
            True if connection successful
        """
        try:
            response = self.quick_response("Hi", max_tokens=5)
            return bool(response and response != "Error generating response.")
        except Exception as e:
            print(f"LLM connection test failed ({self.provider}): {e}")
            return False
