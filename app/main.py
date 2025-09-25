from fastapi import FastAPI

from app.api.routes.ingest import router as ingest_router


def create_app() -> FastAPI:
    app = FastAPI(title="Math Query Assistant - Ingestion Service", version="0.1.0")
    app.include_router(ingest_router, prefix="/api")
    return app


app = create_app()

