"""OpenAI-compatible chat client. Selection and summarization are not implemented yet."""

from typing import Protocol

from lantern.schemas import BriefingItem, Category, Profile, SearchResult


class AIProvider(Protocol):
    def select(
        self,
        *,
        category: Category,
        profile: Profile,
        results: list[SearchResult],
        language: str,
        limit: int,
    ) -> list[BriefingItem]:
        """Choose and summarize items. Cited URLs must come from `results`."""


class OpenAICompatibleProvider:
    def __init__(self, *, api_key: str, base_url: str, model: str, timeout: float) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._timeout = timeout

    def select(
        self,
        *,
        category: Category,
        profile: Profile,
        results: list[SearchResult],
        language: str,
        limit: int,
    ) -> list[BriefingItem]:
        raise NotImplementedError("Model selection is not implemented yet.")

    def __repr__(self) -> str:
        return f"OpenAICompatibleProvider(model={self._model!r})"
