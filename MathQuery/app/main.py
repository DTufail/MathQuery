from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api.routes.ingest import router as ingest_router


def create_app() -> FastAPI:
    app = FastAPI(title="Math Query Assistant - Ingestion API", default_response_class=ORJSONResponse)

    # Routers
    app.include_router(ingest_router, prefix="/api")

    return app


app = create_app()