import io

from pdf2image import convert_from_bytes
from PIL import Image


def pdf_to_images(pdf_bytes: bytes, dpi: int = 200) -> list[Image.Image]:
    """Convert PDF bytes to a list of PIL images, one per page."""
    return convert_from_bytes(pdf_bytes, dpi=dpi)
