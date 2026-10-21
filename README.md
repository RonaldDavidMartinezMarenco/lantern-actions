# Lantern

Lantern is a one-shot personal briefing. It reads a local profile, and will later search the web, skip URLs it already published, summarize the results, and post one message per Discord channel.

The published summary is Spanish (`BRIEFING_LANGUAGE=es`). Code, configuration keys, logs, and this README are English.

This repository currently contains the project skeleton, configuration, and runtime. The briefing pipeline is not implemented yet. `uv run lantern` validates configuration and then exits with an error. `uv run lantern --dry-run` validates configuration and exits successfully, without calling Brave, Gemini, or Discord.

Keep the repository private. `config/profile.toml` contains your career and interests.

## Layout

```text
config/profile.toml          profile
src/lantern/                 package
  config.py                  environment and profile loading
  schemas.py                 shared data contracts
  http.py                    HTTP client defaults
  main.py                    command line
  formatting.py              summary copy
  providers/search.py        Brave
  providers/ai.py            OpenAI-compatible model client
  publishers/discord.py      webhooks
  storage/repository.py      SQLite history
  services/briefing.py       orchestration
tests/                       infrastructure checks
Dockerfile                   one-shot image
docker-compose.yml           local one-shot run
.github/workflows/lantern-briefing.yml
```

## Requirements

- Python 3.12, installed through [uv](https://docs.astral.sh/uv/)
- A private GitHub repository for the scheduled run
- Docker, only if you want the container path

## Setup

```bash
uv sync
```

Credentials live in `.env`, which is gitignored. Start from `.env.example`.

| Variable | Purpose |
| --- | --- |
| `BRAVE_SEARCH_API_KEY` | Brave Search API |
| `GEMINI_API_KEY` | Gemini key used when `LLM_API_KEY` is unset |
| `LLM_API_KEY` | Optional key that overrides `GEMINI_API_KEY` |
| `LLM_BASE_URL` | OpenAI-compatible base URL |
| `LLM_MODEL` | Model name |
| `DISCORD_WEBHOOK_NEWS` | Webhook for `#news` |
| `DISCORD_WEBHOOK_SCHOLARSHIP` | Webhook for `#scholarship` |
| `DISCORD_WEBHOOK_EVENTS` | Webhook for `#events` |
| `BRIEFING_LANGUAGE` | Summary language. `es` is configured |
| `BRIEFING_MAX_RESULTS` | Items the model will be asked to keep. Default `5` |
| `SEARCH_MAX_RESULTS` | Hits requested per search. Default `10` |
| `DATABASE_PATH` | SQLite file. Default `data/lantern.db` |

The checked-in model settings target Gemini's free tier through the OpenAI-compatible endpoint:

```text
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_MODEL=gemini-3.5-flash-lite
```

Edit `config/profile.toml` to change career, country, news topics, scholarship constraints, or event constraints. Category ids are `news`, `scholarship`, and `events`.

## Commands

```bash
uv run lantern --dry-run
uv run lantern --dry-run --category news
uv run pytest
```

`--category` accepts `news`, `scholarship`, or `events`.

Docker runs the same command and mounts `.env`, the profile, and `./data`:

```bash
docker compose run --rm lantern --dry-run
```

## GitHub Actions

The workflow runs at 08:17 America/Bogota (`17 13 * * *` UTC) and can also be started manually. Schedules run only on the default branch.

Add these repository secrets before the first real run:

- `BRAVE_SEARCH_API_KEY`
- `GEMINI_API_KEY`
- `DISCORD_WEBHOOK_NEWS`
- `DISCORD_WEBHOOK_SCHOLARSHIP`
- `DISCORD_WEBHOOK_EVENTS`

`LLM_API_KEY` is optional. `LLM_BASE_URL` and `LLM_MODEL` are set in the workflow file.

GitHub cannot overwrite a cache key, so each run stores `data/lantern.db` under `lantern-sqlite-<run id>` and the next run restores the newest `lantern-sqlite-` entry. Until the pipeline exists, no database file is written and the job fails on purpose when it is dispatched without `--dry-run`.

## Not implemented yet

- Brave queries built from the profile, with a cap per category
- Normalization of title, URL, snippet, source, and date, without inventing a missing date
- SQLite deduplication of URLs already published, including duplicates inside one run
- Model selection of 3 to 5 items per category, rejecting any URL that did not come from Brave
- Spanish Discord messages, split below 2000 characters without cutting an item in half
- Silence for an empty category, and a failed run when Brave, the model, or Discord fails
- Tests for deduplication, invented URLs, empty results, API failures, and the Discord size limit
