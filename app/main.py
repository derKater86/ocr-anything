from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.routes.ocr import router as ocr_router

app = FastAPI(
    title="OCR Everything",
    description="REST API for OCR of images and PDFs using Tesseract.",
    version="1.0.0",
)

app.include_router(ocr_router)


@app.get("/health", tags=["Health"])
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})
