from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, Optional

import httpx
from fastapi import UploadFile


class GrobidClient:
    """Thin async client for GROBID service.

    Exposes `process_fulltext_document` to obtain TEI-XML for a PDF.
    """

    def __init__(self, base_url: str | None = None, timeout_s: float = 60.0) -> None:
        self.base_url = base_url or os.getenv("GROBID_BASE_URL", "http://localhost:8070")
        self.timeout_s = timeout_s

    async def process_fulltext_document(self, file: UploadFile) -> str:
        url = f"{self.base_url}/api/processFulltextDocument"
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            files = {"input": (file.filename, await file.read(), file.content_type)}
            # Reset file to allow re-reads downstream
            await file.seek(0)
            resp = await client.post(url, files=files)
            resp.raise_for_status()
            return resp.text


class GrobidService:
    def __init__(self, client: Optional[GrobidClient] = None) -> None:
        self.client = client or GrobidClient()

    async def extract_structure(self, file: UploadFile) -> str:
        return await self.client.process_fulltext_document(file)


async def get_grobid_service() -> GrobidService:
    # Could add connection checks with timeout
    return GrobidService()

