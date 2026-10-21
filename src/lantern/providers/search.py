"""Brave Search client. The request itself is not implemented yet."""

from typing import Protocol

from lantern.schemas import SearchResult


class SearchProvider(Protocol):
    def search(self, query: str, *, count: int) -> list[SearchResult]:
        """Return normalized hits for one query."""


class BraveSearchProvider:
    def __init__(self, *, api_key: str, timeout: float) -> None:
        self._api_key = api_key
        self._timeout = timeout

    def search(self, query: str, *, count: int) -> list[SearchResult]:
        raise NotImplementedError("Brave search is not implemented yet.")

    def __repr__(self) -> str:
        return "BraveSearchProvider(api_key='***')"
