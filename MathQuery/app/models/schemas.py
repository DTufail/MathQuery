from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Equation(BaseModel):
    latex: str = Field(..., description="Equation in LaTeX format")
    page: Optional[int] = Field(None, description="Page number where equation appears (1-indexed)")
    block_id: Optional[str] = Field(None, description="Optional identifier of the source block or paragraph")
    inline: bool = Field(False, description="True if inline math, False if display math")


class Paragraph(BaseModel):
    id: str
    text: str
    page: Optional[int] = None
    equations: List[Equation] = Field(default_factory=list)


class Section(BaseModel):
    title: Optional[str] = None
    level: Optional[int] = Field(default=None, description="Heading level if known (e.g., 1 for H1)")
    paragraphs: List[Paragraph] = Field(default_factory=list)


class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    pages: Optional[int] = None
    source_filename: Optional[str] = None


class IngestionResult(BaseModel):
    metadata: DocumentMetadata
    sections: List[Section]


class IngestionResponse(BaseModel):
    result: IngestionResult