"""SQLite history of published URLs. Reads and writes are not implemented yet."""

from pathlib import Path
from typing import Protocol

from lantern.schemas import PublishedRecord

PUBLISHED_ITEMS_DDL = """
CREATE TABLE IF NOT EXISTS published_items (
    url TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    published_at TEXT NOT NULL
)
"""


class PublishedItemRepository(Protocol):
    def has_url(self, url: str) -> bool:
        """Return whether this URL was already published."""

    def add(self, record: PublishedRecord) -> None:
        """Store one published URL."""


class SqlitePublishedItemRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def has_url(self, url: str) -> bool:
        raise NotImplementedError("Published-item lookup is not implemented yet.")

    def add(self, record: PublishedRecord) -> None:
        raise NotImplementedError("Published-item storage is not implemented yet.")
