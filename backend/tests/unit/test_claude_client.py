from __future__ import annotations

from collections.abc import Iterator
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services import claude_client, llm_config


@pytest.fixture(autouse=True)
def _isolated_llm_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-5")
    monkeypatch.setenv("ANTHROPIC_MAX_TOKENS", "1024")
    llm_config.get_llm_settings.cache_clear()
    claude_client.get_claude_client.cache_clear()
    yield
    llm_config.get_llm_settings.cache_clear()
    claude_client.get_claude_client.cache_clear()


def _fake_message(text: str) -> SimpleNamespace:
    text_block = SimpleNamespace(type="text", text=text)
    return SimpleNamespace(content=[text_block])


def test_generate_text_returns_concatenated_text_blocks() -> None:
    fake_client = MagicMock()
    fake_client.messages.create.return_value = SimpleNamespace(
        content=[
            SimpleNamespace(type="text", text="Premiere partie."),
            SimpleNamespace(type="text", text="Seconde partie."),
        ]
    )

    result = claude_client.generate_text(
        system_prompt="system",
        user_prompt="user",
        client=fake_client,
    )

    assert result == "Premiere partie.\nSeconde partie."


def test_generate_text_ignores_non_text_blocks() -> None:
    fake_client = MagicMock()
    fake_client.messages.create.return_value = SimpleNamespace(
        content=[
            SimpleNamespace(type="tool_use", text=""),
            SimpleNamespace(type="text", text="Reponse utile."),
        ]
    )

    result = claude_client.generate_text(
        system_prompt="system",
        user_prompt="user",
        client=fake_client,
    )

    assert result == "Reponse utile."


def test_generate_text_calls_messages_create_with_settings() -> None:
    fake_client = MagicMock()
    fake_client.messages.create.return_value = _fake_message("ok")

    claude_client.generate_text(system_prompt="sys", user_prompt="usr", client=fake_client)

    fake_client.messages.create.assert_called_once_with(
        model="claude-sonnet-5",
        max_tokens=1024,
        system="sys",
        messages=[{"role": "user", "content": "usr"}],
    )


def test_get_claude_client_is_cached() -> None:
    first = claude_client.get_claude_client()
    second = claude_client.get_claude_client()

    assert first is second