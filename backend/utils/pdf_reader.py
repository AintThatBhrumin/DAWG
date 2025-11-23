# backend/utils/pdf_reader.py
"""
PDF utilities using PyMuPDF (fitz).
"""

import fitz  # pymupdf

def pdf_to_text(pdf_path: str) -> str:
    """
    Extract selectable text from a PDF. Returns concatenated page text.
    """
    text_chunks = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            try:
                t = page.get_text()
            except Exception:
                t = ""
            if t:
                text_chunks.append(t)
    return "\n".join(text_chunks).strip()


def pdf_has_text(pdf_path: str, min_chars: int = 30) -> bool:
    """
    Return True if PDF contains substantial selectable text.
    """
    try:
        txt = pdf_to_text(pdf_path)
        return len(txt) >= min_chars
    except Exception:
        return False


def pdf_to_images(pdf_path: str, dpi: int = 200) -> list:
    """
    Render PDF pages to PNG files and return list of file paths.
    Caller should remove temp files as needed.
    """
    out = []
    doc = fitz.open(pdf_path)
    tmpdir = "/tmp"  # caller will place under TMP_DIR if desired
    for i, page in enumerate(doc):
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out_path = f"{tmpdir}/dawg_pdf_page_{i+1}.png"
        pix.save(out_path)
        out.append(out_path)
    doc.close()
    return out
