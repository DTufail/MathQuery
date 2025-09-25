from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from starlette import status

from app.schemas.output import IngestionResponse
from app.services.ingestion import IngestionService, get_ingestion_service


router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("/pdf", response_model=IngestionResponse, status_code=status.HTTP_200_OK)
async def ingest_pdf(
    file: UploadFile = File(..., description="PDF file to ingest"),
    service: IngestionService = Depends(get_ingestion_service),
):
    if file.content_type not in {"application/pdf"}:
        raise HTTPException(status_code=400, detail="Only application/pdf is supported")

    try:
        data = await service.ingest_pdf(file)
        return data
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc

