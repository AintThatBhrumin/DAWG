# backend/utils/ocr_reader.py
"""
Image OCR utility using pytesseract and Pillow.
"""

from PIL import Image
import pytesseract

def image_to_text(image_path: str) -> str:
    """
    Extract text from an image path using pytesseract.
    Ensure Tesseract is installed on the system.
    """
    with Image.open(image_path) as img:
        # Optional preprocessing could go here
        text = pytesseract.image_to_string(img)
    return text.strip()


def multiple_images_to_text(image_paths: list) -> str:
    """
    Concatenate OCR outputs from multiple images.
    """
    texts = []
    for p in image_paths:
        try:
            t = image_to_text(p)
            if t:
                texts.append(t)
        except Exception:
            continue
    return "\n".join(texts).strip()
