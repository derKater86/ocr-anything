import io
import time

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from PIL import Image

from app.models.response import OCRResponse, Page
from app.services.ocr_service import ocr_image
from app.services.pdf_service import pdf_to_images

router = APIRouter(prefix="/ocr", tags=["OCR"])

SUPPORTED_IMAGE_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/tiff",
    "image/bmp",
    "image/webp",
}


@router.post("/image", response_model=OCRResponse)
async def ocr_image_endpoint(
    file: UploadFile = File(...),
    language: str = Query(default="eng", description="Tesseract language code (e.g. eng, deu, fra)"),
    structured: bool = Query(default=False, description="Return word-level bounding boxes and confidence scores"),
) -> OCRResponse:
    if file.content_type not in SUPPORTED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. Supported: {sorted(SUPPORTED_IMAGE_TYPES)}",
        )

    start = time.perf_counter()
    contents = await file.read()

    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not open image: {e}")

    try:
        page = ocr_image(image, language=language, structured=structured)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")

    page.page_number = 1
    elapsed_ms = (time.perf_counter() - start) * 1000

    return OCRResponse(
        text=page.text,
        pages=[page],
        language=language,
        processing_time_ms=round(elapsed_ms, 2),
    )


@router.post("/pdf", response_model=OCRResponse)
async def ocr_pdf_endpoint(
    file: UploadFile = File(...),
    language: str = Query(default="eng", description="Tesseract language code (e.g. eng, deu, fra)"),
    structured: bool = Query(default=False, description="Return word-level bounding boxes and confidence scores"),
    dpi: int = Query(default=200, ge=72, le=600, description="DPI for PDF rendering (higher = better quality, slower)"),
) -> OCRResponse:
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="File must be a PDF (application/pdf)")

    start = time.perf_counter()
    contents = await file.read()

    try:
        images = pdf_to_images(contents, dpi=dpi)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse PDF: {e}")

    if not images:
        raise HTTPException(status_code=400, detail="PDF contains no pages")

    pages: list[Page] = []
    for i, img in enumerate(images, start=1):
        try:
            page = ocr_image(img, language=language, structured=structured)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OCR failed on page {i}: {e}")
        page.page_number = i
        pages.append(page)

    full_text = "\n\n".join(p.text for p in pages)
    elapsed_ms = (time.perf_counter() - start) * 1000

    return OCRResponse(
        text=full_text,
        pages=pages,
        language=language,
        processing_time_ms=round(elapsed_ms, 2),
    )
