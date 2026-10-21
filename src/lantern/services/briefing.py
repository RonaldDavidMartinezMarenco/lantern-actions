"""One briefing run. Search, dedup, summary, and publish are not implemented yet."""

from lantern.config import Settings
from lantern.providers.ai import AIProvider
from lantern.providers.search import SearchProvider
from lantern.publishers.discord import Publisher
from lantern.schemas import Category, Profile
from lantern.storage.repository import PublishedItemRepository


class BriefingService:
    def __init__(
        self,
        *,
        settings: Settings,
        profile: Profile,
        search: SearchProvider,
        ai: AIProvider,
        repository: PublishedItemRepository,
        publisher: Publisher,
    ) -> None:
        self._settings = settings
        self._profile = profile
        self._search = search
        self._ai = ai
        self._repository = repository
        self._publisher = publisher

    def run(self, *, category: Category | None, dry_run: bool) -> None:
        raise NotImplementedError(
            "Briefing pipeline is not implemented; nothing was searched or published."
        )
