"""Shared HTTP client settings."""

import httpx

USER_AGENT = "Lantern/0.1"
HTTP_TIMEOUT_SECONDS = 30.0


def make_client(*, timeout: float = HTTP_TIMEOUT_SECONDS) -> httpx.Client:
    """Return a client that identifies itself and does not follow redirects."""

    return httpx.Client(
        timeout=timeout,
        follow_redirects=False,
        headers={"User-Agent": USER_AGENT},
    )
