## Math Query Assistant - Ingestion Service

FastAPI microservice that ingests research PDFs and outputs structured JSON:
- sections
- paragraphs
- equations (LaTeX)
- metadata (page number, section)

### Quickstart

1) Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

2) Start GROBID

```bash
docker compose up -d grobid
```

3) Run API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4) Ingest a PDF

```bash
curl -X POST "http://localhost:8000/api/ingest/pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/paper.pdf" | jq
```

### Configuration

Set credentials in `.env` (or environment):
- `GROBID_BASE_URL` (default `http://localhost:8070`)
- `MATHPIX_APP_ID`, `MATHPIX_APP_KEY` (required)

### Notes
- Initial TEI parsing is minimal; later stories will segment sections/paragraphs using the TEI structure.
- Mathpix plan/response schema varies; the service currently extracts `type: math` blocks.

# MathQuery
