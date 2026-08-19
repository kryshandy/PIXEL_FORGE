"""Thin wrapper around the Anthropic SDK, shared across the application."""

from __future__ import annotations

from functools import lru_cache

from anthropic import Anthropic

from app.services.llm_config import get_llm_settings


@lru_cache
def get_claude_client() -> Anthropic:
    """Return a process-wide Anthropic client, built from `LlmSettings`.

    Cached so the whole application shares a single HTTP client/connection
    pool instead of creating one per request.
    """
    settings = get_llm_settings()
    return Anthropic(api_key=settings.api_key)


def generate_text(
    system_prompt: str,
    user_prompt: str,
    client: Anthropic | None = None,
) -> str:
    """Send a single-turn prompt to Claude and return the text response.

    Args:
        system_prompt: Instructions framing the assistant's role and constraints.
        user_prompt: The user-facing content Claude must respond to.
        client: Anthropic client to use. Defaults to the shared client from
            :func:`get_claude_client`. Overridable for tests.

    Returns:
        The concatenated text of every text block in Claude's response.
    """
    settings = get_llm_settings()
    active_client = client if client is not None else get_claude_client()

    message = active_client.messages.create(
        model=settings.model,
        max_tokens=settings.max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text_blocks = [block.text for block in message.content if block.type == "text"]
    return "\n".join(text_blocks)