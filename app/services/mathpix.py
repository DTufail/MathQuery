from __future__ import annotations

import base64
import os
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException


class MathpixClient:
    """Thin async client for Mathpix OCR API.

    Only the subset we need for equation extraction.
    """

    def __init__(self, app_id: Optional[str] = None, app_key: Optional[str] = None, timeout_s: float = 60.0) -> None:
        self.app_id = app_id or os.getenv("MATHPIX_APP_ID")
        self.app_key = app_key or os.getenv("MATHPIX_APP_KEY")
        self.timeout_s = timeout_s
        self.base_url = os.getenv("MATHPIX_BASE_URL", "https://api.mathpix.com/v3")
        if not self.app_id or not self.app_key:
            raise HTTPException(status_code=500, detail="Mathpix credentials not configured")

    async def ocr_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        url = f"{self.base_url}/text"
        headers = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "Content-Type": "application/json",
        }
        # Use opts focusing on math extraction; keep simple for now
        payload = {
            "src": f"data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode()}",
            "formats": ["text", "data"],
            "math_inline_delimiters": ["$", "$"],
            "rm_spaces": True,
        }
        async with httpx.AsyncClient(timeout=self.timeout_s, headers=headers) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()


class MathpixService:
    def __init__(self, client: Optional[MathpixClient] = None) -> None:
        self.client = client or MathpixClient()

    async def extract_equations(self, pdf_bytes: bytes) -> Dict[str, Any]:
        return await self.client.ocr_pdf(pdf_bytes)


async def get_mathpix_service() -> MathpixService:
    return MathpixService()

