# Math Query Assistant - Ingestion Service

A FastAPI service that ingests a PDF, uses GROBID for structure and Mathpix for equations, and returns structured JSON containing sections, paragraphs, equations (LaTeX), and metadata.

## Features
- FastAPI endpoint to upload PDF and receive structured JSON
- GROBID integration to parse document structure via TEI XML
- Mathpix integration to extract equations (LaTeX); optional if credentials missing
- Modular services and clean Pydantic models

## Setup

### 1) Python environment
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure environment
Copy `.env.example` to `.env` and set values:
```
cp .env.example .env
```
- `MQ_GROBID_URL` should point to your GROBID instance (default `http://localhost:8070`). You can run GROBID via Docker compose from their repo.
- `MQ_MATHPIX_APP_ID` and `MQ_MATHPIX_APP_KEY` are optional; without them, equations list will be empty.

### 3) Run the API
```
uvicorn app.main:app --reload --port 8000
```

### 4) Ingest a PDF
```
curl -X POST "http://localhost:8000/api/ingest" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/paper.pdf;type=application/pdf"
```

Response shape:
```
{
  "result": {
    "metadata": {"title": "...", "authors": ["..."], "pages": 12, "source_filename": "paper.pdf"},
    "sections": [
      {
        "title": "Introduction",
        "level": null,
        "paragraphs": [
          {"id": "p-0-0", "text": "...", "page": null, "equations": [{"latex": "x^2", "page": 2, "inline": false}]}
        ]
      }
    ]
  }
}
```

## Notes
- TEI parsing is intentionally lightweight; you can refine heading levels and page mapping later.
- Equation attachment uses a simple heuristic by page. You can improve mapping using coordinates if available from Mathpix.

## Roadmap
- Improve paragraph-to-page mapping using TEI facsimile coordinates
- Better inline vs display equation detection
- Add unit tests