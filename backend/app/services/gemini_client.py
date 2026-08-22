"""Thin wrapper around the Google Gen AI SDK, shared across the application."""

from __future__ import annotations

from functools import lru_cache

from google import genai
from google.genai import types

from app.services.llm_config import get_llm_settings


@lru_cache
def get_gemini_client() -> genai.Client:
    """Return a process-wide Gemini client, built from `LlmSettings`.

    Cached so the whole application shares a single HTTP client/connection
    pool instead of creating one per request.
    """
    settings = get_llm_settings()
    return genai.Client(api_key=settings.api_key)


def generate_text(
    system_prompt: str,
    user_prompt: str,
    client: genai.Client | None = None,
) -> str:
    """Send a single-turn prompt to Gemini and return the text response.

    Args:
        system_prompt: Instructions framing the assistant's role and constraints.
        user_prompt: The user-facing content Gemini must respond to.
        client: Gemini client to use. Defaults to the shared client from
            :func:`get_gemini_client`. Overridable for tests.

    Returns:
        The text of Gemini's response.
    """
    settings = get_llm_settings()
    active_client = client if client is not None else get_gemini_client()

    response = active_client.models.generate_content(
        model=settings.model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=settings.max_tokens,
            # Gemini 3.x models (incl. gemini-3.6-flash) cannot disable
            # thinking at all -- thinking_budget=0 is a Gemini 2.5-only
            # option and errors out on 3.x (this is why it was reverted in
            # PR #13). The correct 3.x lever is thinking_level: MINIMAL is
            # the lowest available setting. Thinking tokens are still
            # deducted from max_output_tokens even at MINIMAL, so
            # max_tokens is kept generous (see llm_config) as a safety net.
            thinking_config=types.ThinkingConfig(
                thinking_level=types.ThinkingLevel.MINIMAL,
            )
        ),
    )

    return response.text or ""