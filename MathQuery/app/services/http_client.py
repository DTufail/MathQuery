from __future__ import annotations

from typing import Optional

import httpx

from app.core.config import get_settings

_httpx_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    global _httpx_client
    if _httpx_client is None:
        settings = get_settings()
        _httpx_client = httpx.AsyncClient(timeout=settings.request_timeout_seconds)
    return _httpx_client


async def aclose_http_client() -> None:
    global _httpx_client
    if _httpx_client is not None:
        await _httpx_client.aclose()
        _httpx_client = None