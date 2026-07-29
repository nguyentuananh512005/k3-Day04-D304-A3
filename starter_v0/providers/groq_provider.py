from __future__ import annotations

from providers.openai_provider import OpenAIProvider


class GroqProvider(OpenAIProvider):
    """Groq API Provider using OpenAI-compatible Chat Completions endpoint."""

    def __init__(
        self,
        *,
        api_key_env: str = "GROQ_API_KEY",
        base_url: str = "https://api.groq.com/openai/v1",
        default_model: str = "llama-3.1-8b-instant",
    ) -> None:
        super().__init__(
            api_key_env=api_key_env,
            base_url=base_url,
            default_model=default_model,
        )
