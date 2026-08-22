from __future__ import annotations

from collections.abc import Iterator
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services import gemini_client, llm_config


@pytest.fixture(autouse=True)
def _isolated_llm_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.6-flash")
    monkeypatch.setenv("GEMINI_MAX_TOKENS", "1024")
    llm_config.get_llm_settings.cache_clear()
    gemini_client.get_gemini_client.cache_clear()
    yield
    llm_config.get_llm_settings.cache_clear()
    gemini_client.get_gemini_client.cache_clear()


def test_generate_text_returns_response_text() -> None:
    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = SimpleNamespace(text="Reponse utile.")

    result = gemini_client.generate_text(
        system_prompt="system",
        user_prompt="user",
        client=fake_client,
    )

    assert result == "Reponse utile."


def test_generate_text_returns_empty_string_when_response_text_is_none() -> None:
    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = SimpleNamespace(text=None)

    result = gemini_client.generate_text(
        system_prompt="system",
        user_prompt="user",
        client=fake_client,
    )

    assert result == ""


def test_generate_text_calls_generate_content_with_settings() -> None:
    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = SimpleNamespace(text="ok")

    gemini_client.generate_text(system_prompt="sys", user_prompt="usr", client=fake_client)

    call_kwargs = fake_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == "gemini-3.6-flash"
    assert call_kwargs["contents"] == "usr"
    assert call_kwargs["config"].system_instruction == "sys"
    assert call_kwargs["config"].max_output_tokens == 1024
    # gemini-3.6-flash is a Gemini 3.x model: thinking cannot be disabled
    # via thinking_budget=0 (Gemini 2.5-only; errors on 3.x -- this is why
    # it was reverted in PR #13). thinking_level=MINIMAL is the correct 3.x
    # lever to minimize the reasoning tokens deducted from
    # max_output_tokens, which otherwise truncates or empties the visible
    # response (regression: recommendation text was cut off mid-sentence).
    from google.genai import types as genai_types

    assert (
        call_kwargs["config"].thinking_config.thinking_level
        == genai_types.ThinkingLevel.MINIMAL
    )


def test_get_gemini_client_is_cached() -> None:
    first = gemini_client.get_gemini_client()
    second = gemini_client.get_gemini_client()

    assert first is second