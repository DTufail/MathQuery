from __future__ import annotations

from typing import List, Optional

import httpx
from lxml import etree

from app.core.config import get_settings
from app.models.schemas import DocumentMetadata, Paragraph, Section
from app.services.http_client import get_http_client


class GrobidService:
    async def process_pdf_to_tei(self, pdf_bytes: bytes) -> str:
        settings = get_settings()
        client = get_http_client()
        url = f"{settings.grobid_url.rstrip('/')}/api/processFulltextDocument"
        files = {"input": ("document.pdf", pdf_bytes, "application/pdf")}
        data = {"consolidateHeader": 1, "consolidateCitations": 0}
        resp = await client.post(url, files=files, data=data)
        resp.raise_for_status()
        return resp.text

    def parse_tei_to_structure(self, tei_xml: str) -> tuple[DocumentMetadata, List[Section]]:
        root = etree.fromstring(tei_xml.encode("utf-8"))
        ns = {"tei": "http://www.tei-c.org/ns/1.0"}

        # Metadata
        title_nodes = root.xpath("//tei:teiHeader//tei:titleStmt/tei:title/text()", namespaces=ns)
        authors = root.xpath("//tei:teiHeader//tei:author//tei:surname/text() | //tei:teiHeader//tei:author//tei:name/text()", namespaces=ns)
        page_count_nodes = root.xpath("count(//tei:facsimile/tei:surface)", namespaces=ns)
        metadata = DocumentMetadata(
            title=title_nodes[0] if title_nodes else None,
            authors=[a for a in authors if a],
            pages=int(page_count_nodes) if page_count_nodes else None,
        )

        # Sections & paragraphs (very lightweight mapping)
        sections: List[Section] = []
        # Each div[@type='section'] or similar
        for div in root.xpath("//tei:text//tei:body//tei:div", namespaces=ns):
            head = div.xpath("./tei:head/text()", namespaces=ns)
            title = head[0] if head else None
            paras: List[Paragraph] = []
            for idx, p in enumerate(div.xpath(".//tei:p", namespaces=ns)):
                text_content = "".join(p.itertext()).strip()
                if not text_content:
                    continue
                para_id = f"p-{len(sections)}-{idx}"
                # Page info is nontrivial; many TEI outputs do not map p->page plainly.
                paras.append(Paragraph(id=para_id, text=text_content, page=None))
            if paras or title:
                sections.append(Section(title=title, level=None, paragraphs=paras))

        # Fallback if no sections found: take all paragraphs in body
        if not sections:
            paras: List[Paragraph] = []
            for idx, p in enumerate(root.xpath("//tei:text//tei:body//tei:p", namespaces=ns)):
                text_content = "".join(p.itertext()).strip()
                if not text_content:
                    continue
                para_id = f"p-0-{idx}"
                paras.append(Paragraph(id=para_id, text=text_content, page=None))
            if paras:
                sections.append(Section(title=None, level=None, paragraphs=paras))

        return metadata, sections