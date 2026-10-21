from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

from lantern.config import Settings, describe_config_error, load_profile
from lantern.formatting import category_title, opener
from lantern.http import USER_AGENT, make_client
from lantern.main import run
from lantern.providers.ai import OpenAICompatibleProvider
from lantern.providers.search import BraveSearchProvider
from lantern.publishers.discord import DiscordPublisher
from lantern.schemas import Category
from lantern.storage.repository import PUBLISHED_ITEMS_DDL, SqlitePublishedItemRepository

PROFILE_PATH = Path(__file__).parents[1] / "config" / "profile.toml"
WEBHOOK = "https://discord.com/api/webhooks/1/super-secret-token"
FAKE_GEMINI_KEY = "AQ.fake-key-should-not-print"


def _set_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "BSA_test_key")
    monkeypatch.setenv("GEMINI_API_KEY", FAKE_GEMINI_KEY)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("DISCORD_WEBHOOK_NEWS", WEBHOOK)
    monkeypatch.setenv("DISCORD_WEBHOOK_SCHOLARSHIP", WEBHOOK)
    monkeypatch.setenv("DISCORD_WEBHOOK_EVENTS", WEBHOOK)
    monkeypatch.setenv("PROFILE_PATH", str(PROFILE_PATH))
    monkeypatch.setenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
    monkeypatch.setenv("LLM_MODEL", "gemini-3.5-flash-lite")
    monkeypatch.setenv("BRIEFING_LANGUAGE", "es")


def test_profile_contains_the_local_preferences() -> None:
    profile = load_profile(PROFILE_PATH)

    assert profile.language == "es"
    assert profile.identity.career == "Ingeniería de Sistemas"
    assert profile.identity.country == "Colombia"
    assert profile.news.topics == [
        "artificial intelligence",
        "technology",
        "programming",
        "hardware",
    ]
    assert profile.scholarship.levels == ["undergraduate", "research internship"]
    assert profile.scholarship.destination == "Canada"
    assert profile.events.kind == "hackathon"
    assert profile.events.formats == ["online", "in-person"]
    assert profile.events.location == "Barranquilla"
    assert [category.value for category in profile.enabled_categories()] == [
        "news",
        "scholarship",
        "events",
    ]


def test_gemini_key_is_used_when_llm_key_is_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)

    settings = Settings(_env_file=None)

    assert settings.resolved_llm_api_key.get_secret_value() == FAKE_GEMINI_KEY
    assert settings.llm_model == "gemini-3.5-flash-lite"
    assert settings.briefing_language == "es"


def test_llm_api_key_overrides_gemini(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.setenv("LLM_API_KEY", "provider-override")

    settings = Settings(_env_file=None)

    assert settings.resolved_llm_api_key.get_secret_value() == "provider-override"


def test_invalid_webhook_error_hides_the_url(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    secret_url = "https://example.com/super-secret-token"
    monkeypatch.setenv("DISCORD_WEBHOOK_NEWS", secret_url)

    with pytest.raises(ValidationError) as caught:
        Settings(_env_file=None)

    message = describe_config_error(caught.value)
    assert "discord_webhook_news" in message
    assert "super-secret-token" not in message
    assert secret_url not in message


def test_dry_run_reports_readiness_without_secrets(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    _set_required_env(monkeypatch)

    code = run(["--dry-run", "--category", "news"])

    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert code == 0
    assert "Ingeniería de Sistemas" in captured.out
    assert "selected: news" in captured.out
    assert "nothing was searched or published" in captured.out
    assert FAKE_GEMINI_KEY not in combined
    assert "super-secret-token" not in combined
    assert "BSA_test_key" not in combined


def test_real_run_fails_until_the_pipeline_exists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    _set_required_env(monkeypatch)

    code = run([])

    captured = capsys.readouterr()
    assert code == 2
    assert "nothing was searched or published" in captured.err
    assert FAKE_GEMINI_KEY not in captured.out + captured.err


def test_unknown_category_is_rejected() -> None:
    with pytest.raises(SystemExit) as caught:
        run(["--category", "becas"])

    assert caught.value.code == 2


def test_spanish_summary_copy_is_available() -> None:
    assert opener("es").startswith("¡Hola, soy Lan")
    assert category_title("es", Category.NEWS) == "Noticias"
    assert category_title("es", Category.SCHOLARSHIP) == "Becas"
    assert category_title("es", Category.EVENTS) == "Competencias"


def test_http_client_identifies_itself_and_does_not_follow_redirects() -> None:
    client = make_client()
    try:
        assert client.headers["User-Agent"] == USER_AGENT
        assert client.follow_redirects is False
    finally:
        client.close()


def test_pipeline_modules_are_not_implemented(tmp_path: Path) -> None:
    search = BraveSearchProvider(api_key="secret", timeout=1)
    model = OpenAICompatibleProvider(
        api_key="secret",
        base_url="https://example.com/v1",
        model="gemini-3.5-flash-lite",
        timeout=1,
    )
    publisher = DiscordPublisher(webhooks={Category.NEWS: WEBHOOK}, timeout=1)
    repository = SqlitePublishedItemRepository(tmp_path / "lantern.db")

    assert "secret" not in repr(search)
    assert "secret" not in repr(model)
    assert WEBHOOK not in repr(publisher)
    assert "published_items" in PUBLISHED_ITEMS_DDL
    with pytest.raises(NotImplementedError):
        search.search("query", count=1)
    with pytest.raises(NotImplementedError):
        model.select(
            category=Category.NEWS,
            profile=load_profile(PROFILE_PATH),
            results=[],
            language="es",
            limit=5,
        )
    with pytest.raises(NotImplementedError):
        publisher.publish(Category.NEWS, ["hello"])
    with pytest.raises(NotImplementedError):
        repository.has_url("https://example.com")


def test_settings_repr_hides_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    settings = Settings(_env_file=None)

    rendered = repr(settings)
    assert isinstance(settings.brave_search_api_key, SecretStr)
    assert FAKE_GEMINI_KEY not in rendered
    assert "super-secret-token" not in rendered
    assert "BSA_test_key" not in rendered
