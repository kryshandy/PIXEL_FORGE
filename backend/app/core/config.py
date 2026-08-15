"""Environment-driven application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _csv_env(name: str, default: str) -> tuple[str, ...]:
    """Return a normalized tuple from a comma-separated environment variable."""
    raw_value = os.getenv(name, default)
    return tuple(value.strip() for value in raw_value.split(",") if value.strip())


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings with safe local-development defaults."""

    app_name: str
    version: str
    environment: str
    cors_origins: tuple[str, ...]

    @classmethod
    def from_environment(cls) -> Settings:
        return cls(
            app_name=os.getenv("APP_NAME", "Pixel Forge Copilote IA"),
            version=os.getenv("VERSION", "0.1.0"),
            environment=os.getenv("ENVIRONMENT", "development"),
            cors_origins=_csv_env(
                "CORS_ORIGINS",
                "http://localhost:3000,http://localhost:5173",
            ),
        )


@lru_cache
def get_settings() -> Settings:
    """Load settings once per process."""
    return Settings.from_environment()
