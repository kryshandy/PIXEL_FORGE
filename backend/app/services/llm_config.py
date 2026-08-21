"""Environment-driven settings for the Gemini API integration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

_DEFAULT_MODEL = "gemini-3.6-flash"
# Gemini 2.5+/3.x "thinking" models spend part of this budget on internal
# reasoning (thoughtsTokenCount) before writing any visible text: the budget
# is shared, not additive. 1024 was too low and left ~0 tokens for the
# answer once thinking ran, truncating the recommendation mid-sentence.
# Raised as a safety margin on top of disabling thinking in gemini_client.
_DEFAULT_MAX_TOKENS = 2048


@dataclass(frozen=True, slots=True)
class LlmSettings:
    """Runtime settings for calling the Gemini API.

    Attributes:
        api_key: Google AI Studio API key. Required; there is no offline
            fallback for recommendation generation, so a missing key must
            fail loudly rather than silently degrading.
        model: Gemini model used to generate recommendations.
        max_tokens: Maximum tokens generated per recommendation.
    """

    api_key: str
    model: str
    max_tokens: int

    @classmethod
    def from_environment(cls) -> LlmSettings:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY n'est pas configuree. Copier .env.example vers "
                ".env et y renseigner une cle API gratuite (aistudio.google.com/apikey)."
            )
        return cls(
            api_key=api_key,
            model=os.getenv("GEMINI_MODEL", _DEFAULT_MODEL),
            max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", _DEFAULT_MAX_TOKENS)),
        )


@lru_cache
def get_llm_settings() -> LlmSettings:
    """Load LLM settings once per process."""
    return LlmSettings.from_environment()