# backend/routes/upload.py
"""
Upload and extraction routes.
- POST /upload: accepts a file (pdf, image) or text and returns extracted text.
- POST /extract: accepts file or raw text, extracts structured JSON and saves to DB.
"""

import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from database import SessionLocal
from models.invoice import Invoice, Item
from ai_extractor import extract_invoice_auto

# Router for invoice endpoints
router = APIRouter(prefix="/invoices", tags=["invoices"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Temporary upload folder
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/invoice_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: Optional[UploadFile] = File(None), text: Optional[str] = Form(None)):
    """
    Accepts a file or raw text and returns extracted text.
    Use this endpoint when you only want the raw extracted text (no DB save).
    """
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide a file or a text field.")

    if text:
        return {"text": text}

    # Save file
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    dest_path = os.path.join(UPLOAD_DIR, filename)
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    lower = file.filename.lower()
    try:
        if lower.endswith(".pdf"):
            from utils.pdf_reader import pdf_to_text
            extracted = pdf_to_text(dest_path)
        elif lower.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
            from utils.ocr_reader import image_to_text
            extracted = image_to_text(dest_path)
        else:
            with open(dest_path, "r", encoding="utf-8", errors="ignore") as f:
                extracted = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {e}")

    return {"text": extracted}


@router.post("/extract")
async def extract_and_save(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Accepts either text or a file (PDF/image). Runs extraction and saves Invoice + Items to DB.
    """
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide either text or a file.")

    saved_temp_path = None

    # If raw text provided, call extractor in text mode
    if text:
        try:
            structured = extract_invoice_auto(text, is_text=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI extraction failed: {e}")
    else:
        # Save uploaded file to disk
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        dest_path = os.path.join(UPLOAD_DIR, filename)
        saved_temp_path = dest_path
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Call unified extractor which will handle pdf/image/text file
        try:
            structured = extract_invoice_auto(dest_path, is_text=False)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI extraction failed: {e}")

    # Validate structured is a dict
    if not isinstance(structured, dict):
        raise HTTPException(status_code=500, detail="AI returned invalid format (expected JSON object).")

    # Persist to database
    try:
        invoice = Invoice(
            invoice_number=structured.get("invoice_number"),
            vendor_name=structured.get("vendor_name"),
            buyer_name=structured.get("buyer_name"),
            date=structured.get("date"),
            subtotal=_safe_cast_float(structured.get("subtotal")),
            tax=_safe_cast_float(structured.get("tax")),
            total=_safe_cast_float(structured.get("total")),
            currency=structured.get("currency"),
            raw_text=structured.get("raw_text")
        )
        db.add(invoice)
        db.flush()  # to get invoice.id

        items = structured.get("items") or []
        for it in items:
            item = Item(
                invoice_id=invoice.id,
                name=it.get("name"),
                quantity=_safe_cast_float(it.get("quantity")),
                unit_price=_safe_cast_float(it.get("unit_price")),
                total_price=_safe_cast_float(it.get("total_price"))
            )
            db.add(item)

        db.commit()
        db.refresh(invoice)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save invoice to DB: {e}")

    # Optionally cleanup temp file
    if saved_temp_path and os.path.exists(saved_temp_path):
        try:
            os.remove(saved_temp_path)
        except Exception:
            pass

    return JSONResponse(content={
        "invoice_id": invoice.id,
        "invoice": {
            "invoice_number": invoice.invoice_number,
            "vendor_name": invoice.vendor_name,
            "buyer_name": invoice.buyer_name,
            "date": invoice.date,
            "subtotal": invoice.subtotal,
            "tax": invoice.tax,
            "total": invoice.total,
            "currency": invoice.currency,
        },
        "items_saved": len(items),
        "structured": structured
    })


def _safe_cast_float(val):
    if val is None:
        return None
    try:
        return float(val)
    except Exception:
        s = str(val)
        s = re.sub(r"[^\d\.\-]", "", s)
        try:
            return float(s) if s not in ("", ".", "-") else None
        except Exception:
            return None
