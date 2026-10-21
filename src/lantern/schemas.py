"""Data contracts for a briefing run."""

from datetime import date, datetime
from enum import Enum

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class Category(str, Enum):
    NEWS = "news"
    SCHOLARSHIP = "scholarship"
    EVENTS = "events"


class Identity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    career: str = Field(min_length=1)
    country: str = Field(min_length=1)


class NewsPreferences(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    topics: list[str] = Field(min_length=1)


class ScholarshipPreferences(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    levels: list[str] = Field(min_length=1)
    destination: str = Field(min_length=1)


class EventPreferences(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    kind: str = Field(min_length=1)
    formats: list[str] = Field(min_length=1)
    location: str = Field(min_length=1)


class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language: str = Field(min_length=2, max_length=12)
    identity: Identity
    news: NewsPreferences
    scholarship: ScholarshipPreferences
    events: EventPreferences

    def enabled_categories(self) -> list[Category]:
        selected: list[Category] = []
        if self.news.enabled:
            selected.append(Category.NEWS)
        if self.scholarship.enabled:
            selected.append(Category.SCHOLARSHIP)
        if self.events.enabled:
            selected.append(Category.EVENTS)
        return selected


class SearchResult(BaseModel):
    """One normalized search hit. `published_on` stays empty when the source has no date."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    url: AnyHttpUrl
    snippet: str
    source: str | None = None
    published_on: date | None = None


class BriefingItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    url: AnyHttpUrl
    summary: str = Field(min_length=1)
    source: str | None = None


class PublishedRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: AnyHttpUrl
    category: Category
    title: str = Field(min_length=1)
    published_at: datetime
