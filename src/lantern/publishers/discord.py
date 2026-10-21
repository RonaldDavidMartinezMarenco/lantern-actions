"""Discord webhook publisher. Posting is not implemented yet."""

from typing import Protocol

from lantern.schemas import Category


class Publisher(Protocol):
    def publish(self, category: Category, messages: list[str]) -> None:
        """Send already formatted messages to one category channel."""


class DiscordPublisher:
    def __init__(self, *, webhooks: dict[Category, str], timeout: float) -> None:
        self._webhooks = webhooks
        self._timeout = timeout

    def publish(self, category: Category, messages: list[str]) -> None:
        raise NotImplementedError("Discord publishing is not implemented yet.")

    def __repr__(self) -> str:
        names = ", ".join(category.value for category in self._webhooks)
        return f"DiscordPublisher(categories=[{names}])"
