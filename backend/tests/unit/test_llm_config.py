from __future__ import annotations

from collections.abc import Iterator

import pytest

from app.services import llm_config


@pytest.fixture(autouse=True)
def _clear_cache() -> Iterator[None]:
    llm_config.get_llm_settings.cache_clear()
    yield
    llm_config.get_llm_settings.cache_clear()


def test_from_environment_raises_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        llm_config.LlmSettings.from_environment()


def test_from_environment_reads_configured_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.6-flash")
    monkeypatch.setenv("GEMINI_MAX_TOKENS", "2048")

    settings = llm_config.LlmSettings.from_environment()

    assert settings.api_key == "test-key"
    assert settings.model == "gemini-3.6-flash"
    assert settings.max_tokens == 2048


def test_from_environment_uses_default_model_and_max_tokens(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("GEMINI_MAX_TOKENS", raising=False)

    settings = llm_config.LlmSettings.from_environment()

    assert settings.model == "gemini-3.6-flash"
    assert settings.max_tokens == 3072


def test_get_llm_settings_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    first = llm_config.get_llm_settings()
    second = llm_config.get_llm_settings()

    assert first is second