# backend/splitter.py
import re
import os
from typing import List, Tuple
from utils.pdf_reader import pdf_has_text, pdf_to_text, pdf_to_images
from utils.ocr_reader import multiple_images_to_text

# Heuristics/separators that commonly indicate invoice boundaries.
BOUNDARY_KEYWORDS = [
    r"\bTAX\s+INVOICE\b",
    r"\bBILL\s+OF\s+SUPPLY\b",
    r"\bINVOICE\s+NO\b",
    r"\bInvoice Number\b",
    r"\bInvoice No\b",
    r"\bInvoice\s*:\b",
    r"\bORDER\s+NUMBER\b",
    r"\bGSTIN\b",
    r"\bBill To\b",
    r"\bSold By\b",
    r"\bTax Invoice\b"
]

COMPILED_BOUNDARIES = re.compile("|".join(BOUNDARY_KEYWORDS), flags=re.IGNORECASE)

def find_boundaries(text: str) -> List[int]:
    """Return a sorted list of match start indices for the boundary keywords."""
    matches = [m.start() for m in COMPILED_BOUNDARIES.finditer(text)]
    matches = sorted(set(matches))
    return matches

def split_text_by_boundaries(text: str) -> List[str]:
    """
    Split text into sections by boundaries found. Keeps context: each boundary becomes start of a section.
    """
    indices = find_boundaries(text)
    if not indices:
        return [text]

    sections = []
    indices.append(len(text))
    start = 0
    for idx in indices:
        if idx <= start:
            continue
        sec = text[start:idx].strip()
        if sec:
            sections.append(sec)
        start = idx
    # append final tail
    tail = text[start:].strip()
    if tail:
        sections.append(tail)
    # If initial patch caused the first section to be a header-only fragment, merge small fragments
    cleaned = []
    for s in sections:
        if cleaned and len(s.split()) < 5:
            cleaned[-1] += "\n\n" + s
        else:
            cleaned.append(s)
    return cleaned

def split_pdf_into_sections(pdf_path: str) -> List[Tuple[int, str]]:
    """
    Returns list of (section_id, text). Uses selectable text if possible, otherwise OCR.
    """
    if pdf_has_text(pdf_path):
        text = pdf_to_text(pdf_path)
    else:
        image_pages = pdf_to_images(pdf_path)
        text = multiple_images_to_text(image_pages)

    # Normalize whitespace
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    sections = split_text_by_boundaries(text)
    # If no boundaries detected but file contains multiple 'Invoice Number' occurrences, split by those:
    if len(sections) == 1:
        # fallback: split by repeated "Invoice" tokens
        parts = re.split(r"(?i)(\bInvoice\b|\bInvoice Number\b|\bINVOICE\b)", text)
        # reconstruct in chunks
        if len(parts) > 3:
            # crude reconstruction: find occurrences of 'Invoice' and split there
            idxs = [m.start() for m in re.finditer(r"(?i)\bInvoice\b", text)]
            if len(idxs) > 1:
                # use indices to cut slices
                indices = idxs + [len(text)]
                sects = []
                s0 = 0
                for i in indices:
                    if i <= s0:
                        continue
                    sects.append(text[s0:i].strip())
                    s0 = i
                if s0 < len(text):
                    sects.append(text[s0:].strip())
                sections = [s for s in sects if len(s.split()) > 10]
    # Provide ids
    result = [(i+1, s) for i, s in enumerate(sections)]
    return result
