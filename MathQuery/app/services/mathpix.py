from __future__ import annotations

from typing import List

import httpx

from app.core.config import get_settings
from app.models.schemas import Equation
from app.services.http_client import get_http_client


class MathpixService:
    async def extract_equations(self, pdf_bytes: bytes) -> List[Equation]:
        settings = get_settings()
        if not settings.mathpix_app_id or not settings.mathpix_app_key:
            return []

        # Using v3/text with PDF input extracts text and LaTeX; post-processing to find equations can be refined later.
        client = get_http_client()
        url = "https://api.mathpix.com/v3/text"
        headers = {
            "app_id": settings.mathpix_app_id,
            "app_key": settings.mathpix_app_key,
        }
        files = {"file": ("document.pdf", pdf_bytes, "application/pdf")}
        data = {"formats": ["text", "latex_normal"], "math_inline_delimiters": ["$", "$"]}
        resp = await client.post(url, headers=headers, files=files, data={"options_json": httpx.dumps(data)})
        # If Mathpix returns 4xx due to quota or config, swallow and return no equations
        if resp.status_code >= 400:
            return []
        payload = resp.json()
        # payload structure varies; we will conservatively pull 'latex_normal' blocks
        equations: List[Equation] = []
        try:
            pages = payload.get("pages") or []
            for page_index, page in enumerate(pages, start=1):
                for block in page.get("blocks", []):
                    latex_value = block.get("latex_normal") or block.get("latex_styled")
                    if latex_value:
                        equations.append(Equation(latex=latex_value, page=page_index, block_id=str(block.get("id")), inline=False))
        except Exception:
            return []
        return equations