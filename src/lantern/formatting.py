"""User-facing briefing copy. Summaries are Spanish when language is `es`."""

from lantern.schemas import Category

DISCORD_MESSAGE_LIMIT = 2000

OPENERS: dict[str, str] = {
    "es": "¡Hola, soy Lan del proyecto Lantern, aquí está tu resumen!",
}

CATEGORY_TITLES: dict[str, dict[Category, str]] = {
    "es": {
        Category.NEWS: "Noticias",
        Category.SCHOLARSHIP: "Becas",
        Category.EVENTS: "Competencias",
    },
}


def opener(language: str) -> str:
    try:
        return OPENERS[language]
    except KeyError as exc:
        raise NotImplementedError(f"No briefing opener for language: {language}") from exc


def category_title(language: str, category: Category) -> str:
    try:
        return CATEGORY_TITLES[language][category]
    except KeyError as exc:
        raise NotImplementedError(
            f"No category title for language={language} category={category.value}"
        ) from exc


def format_briefing(
    *,
    language: str,
    category: Category,
    profile_line: str,
    items: list[object],
) -> list[str]:
    """Split a category briefing into Discord messages. Not implemented yet."""

    raise NotImplementedError("Briefing formatting is not implemented yet.")
