"""Command line entry point.

The briefing pipeline is intentionally not executed yet. This command loads
configuration and reports that search, summary, and publishing are pending.
"""

import argparse
import sys
from urllib.parse import urlparse

from pydantic import ValidationError

from lantern.config import Settings, describe_config_error, load_profile
from lantern.http import HTTP_TIMEOUT_SECONDS
from lantern.providers.ai import OpenAICompatibleProvider
from lantern.providers.search import BraveSearchProvider
from lantern.publishers.discord import DiscordPublisher
from lantern.schemas import Category, Profile
from lantern.services.briefing import BriefingService
from lantern.storage.repository import SqlitePublishedItemRepository


def run(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        settings = Settings()
    except ValidationError as exc:
        print(describe_config_error(exc), file=sys.stderr)
        return 1

    try:
        profile = load_profile(settings.profile_path)
    except FileNotFoundError:
        print(f"Profile file not found: {settings.profile_path}", file=sys.stderr)
        return 1
    except ValidationError as exc:
        print(describe_config_error(exc), file=sys.stderr)
        return 1

    selected: Category | None = None
    if args.category is not None:
        selected = Category(args.category)
        if selected not in profile.enabled_categories():
            print(f"Category is disabled in the profile: {selected.value}", file=sys.stderr)
            return 1

    print(_status(settings, profile, selected))
    service = _service(settings, profile)
    try:
        service.run(category=selected, dry_run=args.dry_run)
    except NotImplementedError as exc:
        stream = sys.stdout if args.dry_run else sys.stderr
        print(exc, file=stream)
        return 0 if args.dry_run else 2
    return 0


def main() -> None:
    sys.exit(run())


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lantern",
        description="Load Lantern configuration. The briefing pipeline is not implemented yet.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration without treating a missing pipeline as a failure.",
    )
    parser.add_argument(
        "--category",
        choices=[category.value for category in Category],
        help="Limit a future run to one category.",
    )
    return parser


def _status(settings: Settings, profile: Profile, category: Category | None) -> str:
    host = urlparse(settings.llm_base_url)
    lines = [
        "Lantern infrastructure check",
        f"summary_language: {settings.briefing_language}",
        f"llm_host: {host.scheme}://{host.netloc}",
        f"model: {settings.llm_model}",
        f"career: {profile.identity.career}",
        f"country: {profile.identity.country}",
        "categories: " + ", ".join(item.value for item in profile.enabled_categories()),
        "credentials: brave=yes llm=yes webhooks=3",
        f"selected: {category.value if category else 'all'}",
    ]
    if settings.briefing_language != profile.language:
        lines.insert(2, f"profile_language: {profile.language}")
    return "\n".join(lines)


def _service(settings: Settings, profile: Profile) -> BriefingService:
    return BriefingService(
        settings=settings,
        profile=profile,
        search=BraveSearchProvider(
            api_key=settings.brave_search_api_key.get_secret_value(),
            timeout=HTTP_TIMEOUT_SECONDS,
        ),
        ai=OpenAICompatibleProvider(
            api_key=settings.resolved_llm_api_key.get_secret_value(),
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            timeout=HTTP_TIMEOUT_SECONDS,
        ),
        repository=SqlitePublishedItemRepository(settings.database_path),
        publisher=DiscordPublisher(
            webhooks={
                Category.NEWS: settings.discord_webhook_news.get_secret_value(),
                Category.SCHOLARSHIP: settings.discord_webhook_scholarship.get_secret_value(),
                Category.EVENTS: settings.discord_webhook_events.get_secret_value(),
            },
            timeout=HTTP_TIMEOUT_SECONDS,
        ),
    )


if __name__ == "__main__":
    main()
