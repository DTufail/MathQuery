from __future__ import annotations

import hashlib
import io
from typing import List, Optional

from fastapi import Depends, HTTPException, UploadFile

from app.schemas.output import DocumentMetadata, Equation, IngestionResponse, Paragraph, Section
from app.services.grobid import GrobidService, get_grobid_service
from app.services.mathpix import MathpixService, get_mathpix_service


class IngestionService:
    def __init__(
        self,
        grobid: GrobidService = Depends(get_grobid_service),
        mathpix: MathpixService = Depends(get_mathpix_service),
    ) -> None:
        self.grobid = grobid
        self.mathpix = mathpix

    async def ingest_pdf(self, file: UploadFile) -> IngestionResponse:
        pdf_bytes = await file.read()
        await file.seek(0)

        # 1) Structure via GROBID (TEI XML). Parsing to sections kept minimal initially.
        tei_xml = await self.grobid.extract_structure(file)

        # 2) Equations via Mathpix
        mathpix_data = await self.mathpix.extract_equations(pdf_bytes)

        # 3) Map into our schema. Minimal placeholder mapping; refine later with TEI parsing.
        sections: List[Section] = []
        paragraphs: List[Paragraph] = []
        equations: List[Equation] = []

        # Parse Mathpix response for equations; structure assumptions may vary by plan tier.
        # We look for blocks with type 'math' and extract LaTeX; otherwise skip.
        blocks = (mathpix_data or {}).get("data", [])
        for idx, block in enumerate(blocks):
            if block.get("type") == "math":
                latex = block.get("value") or block.get("latex") or ""
                if not latex:
                    continue
                page = int(block.get("page", 1)) if block.get("page") else 1
                display = bool(block.get("display", True))
                eq_id = hashlib.sha1(f"{page}:{idx}:{latex}".encode()).hexdigest()[:12]
                equations.append(
                    Equation(
                        id=eq_id,
                        latex=latex,
                        display=display,
                        page=page,
                        section=None,
                        context_snippet=block.get("text") or None,
                    )
                )

        # Minimal document metadata until TEI parsing added
        metadata = DocumentMetadata(title=None, authors=[], num_pages=None)

        # For now, a single implicit section with all content; to be replaced by TEI parsing
        if equations or paragraphs:
            sections.append(
                Section(
                    id="sec-1",
                    title="Document",
                    page_start=1,
                    page_end=None,
                    paragraphs=paragraphs,
                )
            )

        return IngestionResponse(metadata=metadata, sections=sections)


async def get_ingestion_service(
    grobid: GrobidService = Depends(get_grobid_service),
    mathpix: MathpixService = Depends(get_mathpix_service),
) -> IngestionService:
    return IngestionService(grobid=grobid, mathpix=mathpix)

