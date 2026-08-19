"""Environment-driven settings for the Claude API integration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

_DEFAULT_MODEL = "claude-sonnet-5"
_DEFAULT_MAX_TOKENS = 1024


@dataclass(frozen=True, slots=True)
class LlmSettings:
    """Runtime settings for calling the Claude API.

    Attributes:
        api_key: Anthropic API key. Required; there is no offline fallback
            for recommendation generation, so a missing key must fail loudly
            rather than silently degrading.
        model: Claude model used to generate recommendations.
        max_tokens: Maximum tokens generated per recommendation.
    """

    api_key: str
    model: str
    max_tokens: int

    @classmethod
    def from_environment(cls) -> LlmSettings:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY n'est pas configuree. Copier .env.example vers "
                ".env et y renseigner une cle API valide (console.anthropic.com)."
            )
        return cls(
            api_key=api_key,
            model=os.getenv("ANTHROPIC_MODEL", _DEFAULT_MODEL),
            max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", _DEFAULT_MAX_TOKENS)),
        )


@lru_cache
def get_llm_settings() -> LlmSettings:
    """Load LLM settings once per process."""
    return LlmSettings.from_environment()