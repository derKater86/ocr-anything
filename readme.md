# OCR ANYTHING
## 🐳 Docker based REST API Tool for text extraction
[![Version](https://img.shields.io/badge/tesseract-5.4.2-orange)](https://github.com/tesseract-ocr/tesseract/releases)
[![Version](https://img.shields.io/badge/fastapi-0.132-green)](https://github.com/tesseract-ocr/tesseract/releases)

## Features
- 🏞️ **Image OCR**: OCR Images like jpeg, png and convert it to text
- 📄 **PDF OCR**: OCR PDFs page-by-page and convert it to text
- 🌍 **Multi-language**: All Tesseract language packs preinstalled (e.g. `eng`, `deu`, `fra`, `spa`, ...)
- 📐 **Structured output**: Optional word-level bounding boxes and confidence scores

## Quickstart

Run the prebuilt image from GitHub Container Registry — no clone needed:

```bash
mkdir ocr-everything && cd ocr-everything
curl -O https://raw.githubusercontent.com/derKater86/ocr-everything/main/docker-compose.yml
docker compose pull
docker compose up -d
```

The API is then available at **http://localhost:5555**.

Quick smoke test:

```bash
curl http://localhost:5555/health
# {"status":"ok"}
```

Interactive Swagger docs: **http://localhost:5555/docs**

## Install

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) (>= 20.10)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2+)

### Option A — Docker Compose (recommended)

Use the prebuilt image from [GitHub Container Registry](https://github.com/derKater86/ocr-everything/pkgs/container/ocr-everything):

```bash
curl -O https://raw.githubusercontent.com/derKater86/ocr-everything/main/docker-compose.yml
docker compose pull
docker compose up -d
```

The compose file:
- pulls `ghcr.io/derkater86/ocr-everything:latest`
- exposes port **5555** on the host (mapped to container port `8000`)
- adds a healthcheck against `/health`
- restarts automatically unless explicitly stopped

To update later:

```bash
docker compose pull && docker compose up -d
```

To stop:

```bash
docker compose down
```

### Option B — Build from source

For development or customization, clone and build locally:

```bash
git clone https://github.com/derKater86/ocr-everything.git
cd ocr-everything
docker compose up -d --build
```

This builds an image based on `python:3.12-slim` with:
- `tesseract-ocr` + all language packs
- `poppler-utils` (for PDF rendering)
- the FastAPI app

Because the compose file declares both `image:` and `build:`, `docker compose up --build` produces a local image tagged as `ghcr.io/derkater86/ocr-everything:latest` — `docker compose up` afterwards reuses it without pulling.

### Changing the host port

Edit [docker-compose.yml](docker-compose.yml) — change the left side of `"5555:8000"` to whatever port you want exposed on the host.

## How to Use

The API exposes three endpoints:

| Method | Path         | Description                              |
|--------|--------------|------------------------------------------|
| GET    | `/health`    | Health check                             |
| POST   | `/ocr/image` | OCR a single image (png, jpeg, tiff, …)  |
| POST   | `/ocr/pdf`   | OCR a PDF (one OCR result per page)      |

### OCR an Image

```bash
curl -X POST "http://localhost:5555/ocr/image?language=eng" \
  -F "file=@/path/to/your/image.png"
```

**Query parameters:**
- `language` (default `eng`) — Tesseract language code (`eng`, `deu`, `fra`, `spa`, …)
- `structured` (default `false`) — if `true`, returns word-level bounding boxes + confidence

**Supported image types:** `image/png`, `image/jpeg`, `image/jpg`, `image/tiff`, `image/bmp`, `image/webp`

### OCR a PDF

```bash
curl -X POST "http://localhost:5555/ocr/pdf?language=eng&dpi=200" \
  -F "file=@/path/to/your/document.pdf"
```

**Query parameters:**
- `language` (default `eng`) — Tesseract language code
- `structured` (default `false`) — word-level bounding boxes + confidence
- `dpi` (default `200`, range `72`–`600`) — rendering DPI per page (higher = better quality, slower)

### Response Format

```json
{
  "text": "Hello OCR World!\nOCR Everything works.",
  "pages": [
    {
      "page_number": 1,
      "text": "Hello OCR World!\nOCR Everything works.",
      "words": null
    }
  ],
  "language": "eng",
  "processing_time_ms": 118.36
}
```

With `structured=true`, each page additionally contains a `words` array:

```json
{
  "words": [
    {
      "text": "Hello",
      "confidence": 96.0,
      "bounding_box": { "x": 23, "y": 57, "width": 73, "height": 25 }
    }
  ]
}
```

### Error Responses

| Status | Meaning                                        |
|--------|------------------------------------------------|
| 400    | File could not be opened / PDF has no pages    |
| 415    | Unsupported file type                          |
| 500    | OCR failure                                    |

## License
NOTE: This software depends on other packages that may be licensed under different open source licenses.
