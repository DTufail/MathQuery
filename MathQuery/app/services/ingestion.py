from __future__ import annotations

from typing import List

from app.models.schemas import Equation, IngestionResult, Paragraph, Section
from app.services.grobid import GrobidService
from app.services.mathpix import MathpixService


class IngestionService:
    def __init__(self) -> None:
        self._grobid = GrobidService()
        self._mathpix = MathpixService()

    async def ingest_pdf(self, pdf_bytes: bytes, filename: str | None = None) -> IngestionResult:
        tei_xml = await self._grobid.process_pdf_to_tei(pdf_bytes)
        metadata, sections = self._grobid.parse_tei_to_structure(tei_xml)
        metadata.source_filename = filename

        equations = await self._mathpix.extract_equations(pdf_bytes)
        merged_sections = self._merge_equations(sections, equations)
        return IngestionResult(metadata=metadata, sections=merged_sections)

    def _merge_equations(self, sections: List[Section], equations: List[Equation]) -> List[Section]:
        # Simple heuristic: attach equations to the nearest paragraph on the same page (if page known); otherwise attach to first section.
        if not equations:
            return sections

        # Build list of paragraphs with page numbers
        paragraphs: List[Paragraph] = []
        for section in sections:
            paragraphs.extend(section.paragraphs)

        for eq in equations:
            attached = False
            if eq.page is not None:
                for para in paragraphs:
                    if para.page == eq.page:
                        para.equations.append(eq)
                        attached = True
                        break
            if not attached and paragraphs:
                paragraphs[0].equations.append(eq)
        return sections