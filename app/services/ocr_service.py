import pytesseract
from PIL import Image

from app.models.response import BoundingBox, Page, Word


def ocr_image(image: Image.Image, language: str, structured: bool) -> Page:
    """Run Tesseract OCR on a PIL image and return a Page result."""
    if structured:
        data = pytesseract.image_to_data(
            image,
            lang=language,
            output_type=pytesseract.Output.DICT,
        )
        words: list[Word] = []
        full_text_parts: list[str] = []

        for i, word_text in enumerate(data["text"]):
            if not word_text.strip():
                continue
            conf = float(data["conf"][i])
            if conf < 0:
                continue
            words.append(
                Word(
                    text=word_text,
                    confidence=conf,
                    bounding_box=BoundingBox(
                        x=data["left"][i],
                        y=data["top"][i],
                        width=data["width"][i],
                        height=data["height"][i],
                    ),
                )
            )
            full_text_parts.append(word_text)

        text = " ".join(full_text_parts)
        return Page(page_number=1, text=text, words=words)

    text = pytesseract.image_to_string(image, lang=language)
    return Page(page_number=1, text=text.strip())
