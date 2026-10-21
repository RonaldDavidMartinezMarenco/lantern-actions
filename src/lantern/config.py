"""Environment settings and profile loading."""

import re
import tomllib
from pathlib import Path
from typing import Self
from urllib.parse import urlparse

from pydantic import Field, SecretStr, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from lantern.schemas import Profile

_WEBHOOK_URL = re.compile(r"^https://discord\.com/api/webhooks/\d+/[\w.-]+$")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    brave_search_api_key: SecretStr
    gemini_api_key: SecretStr | None = None
    llm_api_key: SecretStr | None = None
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    llm_model: str = Field(default="gemini-3.5-flash-lite", min_length=1)
    discord_webhook_news: SecretStr
    discord_webhook_scholarship: SecretStr
    discord_webhook_events: SecretStr
    briefing_language: str = Field(default="es", min_length=2, max_length=12)
    briefing_max_results: int = Field(default=5, ge=1, le=10)
    search_max_results: int = Field(default=10, ge=1, le=20)
    database_path: Path = Path("data/lantern.db")
    profile_path: Path = Path("config/profile.toml")

    @field_validator("gemini_api_key", "llm_api_key", mode="before")
    @classmethod
    def blank_secret_is_missing(cls, value: object) -> object:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @field_validator(
        "discord_webhook_news",
        "discord_webhook_scholarship",
        "discord_webhook_events",
    )
    @classmethod
    def webhook_url(cls, value: SecretStr) -> SecretStr:
        if _WEBHOOK_URL.fullmatch(value.get_secret_value()) is None:
            raise ValueError("must be a Discord webhook URL")
        return value

    @field_validator("llm_base_url")
    @classmethod
    def https_base_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("must be an https URL without credentials")
        return value.rstrip("/")

    @model_validator(mode="after")
    def require_model_key(self) -> Self:
        if self.llm_api_key is None and self.gemini_api_key is None:
            raise ValueError("LLM_API_KEY or GEMINI_API_KEY is required")
        return self

    @property
    def resolved_llm_api_key(self) -> SecretStr:
        if self.llm_api_key is not None:
            return self.llm_api_key
        if self.gemini_api_key is not None:
            return self.gemini_api_key
        raise ValueError("LLM_API_KEY or GEMINI_API_KEY is required")


def load_profile(path: Path) -> Profile:
    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    return Profile.model_validate(payload)


def describe_config_error(exc: ValidationError) -> str:
    """Format a settings or profile error without echoing secret values."""

    parts: list[str] = []
    for error in exc.errors():
        location = ".".join(str(item) for item in error["loc"]) or "settings"
        message = str(error.get("msg", "invalid"))
        if "://" in message or "http" in message.lower() or len(message) > 120:
            message = "invalid value"
        parts.append(f"{location}: {message}")
    return "Invalid configuration: " + "; ".join(parts)
