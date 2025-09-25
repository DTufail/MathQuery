from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import IngestionResponse
from app.services.ingestion import IngestionService

router = APIRouter(tags=["ingestion"])


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_pdf(file: UploadFile = File(...)) -> Any:
    if file.content_type not in ("application/pdf", "application/x-pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    pdf_bytes = await file.read()

    service = IngestionService()
    try:
        result = await service.ingest_pdf(pdf_bytes=pdf_bytes, filename=file.filename)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return IngestionResponse(result=result)