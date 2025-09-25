from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Equation(BaseModel):
    id: str = Field(..., description="Stable equation identifier")
    latex: str = Field(..., description="Equation in LaTeX")
    display: bool = Field(..., description="True if display math, False if inline")
    page: int = Field(..., ge=1, description="1-based page number")
    section: Optional[str] = Field(None, description="Section heading where equation appears")
    context_snippet: Optional[str] = Field(None, description="Surrounding text snippet")


class Paragraph(BaseModel):
    id: str
    text: str
    page: int = Field(..., ge=1)
    section: Optional[str] = None
    equations: List[Equation] = Field(default_factory=list)


class Section(BaseModel):
    id: str
    title: str
    page_start: int = Field(..., ge=1)
    page_end: Optional[int] = Field(None, ge=1)
    paragraphs: List[Paragraph] = Field(default_factory=list)


class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    num_pages: Optional[int] = None


class IngestionResponse(BaseModel):
    metadata: DocumentMetadata
    sections: List[Section]

