from pydantic import BaseModel


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class Word(BaseModel):
    text: str
    confidence: float
    bounding_box: BoundingBox


class Page(BaseModel):
    page_number: int
    text: str
    words: list[Word] | None = None


class OCRResponse(BaseModel):
    text: str
    pages: list[Page]
    language: str
    processing_time_ms: float
