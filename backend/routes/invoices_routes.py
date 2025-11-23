"""
DAWG/backend/app/routes/invoices.py

Routes:
- POST /api/invoices/upload   -> upload file, extract text, call AI, save invoice+items
- POST /api/invoices/extract  -> accept {"text": "..."} -> parse via AI and return JSON (no save)
- GET  /api/invoices/         -> list invoices
- GET  /api/invoices/{id}     -> get invoice by id
"""
import os
import uuid
from typing import List

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.invoice import Invoice, Item
from ..schemas.invoice_schema import InvoiceOut
from ..utils import ocr, file_helpers
from .. import ai_extractor

router = APIRouter()

@router.post("/upload", response_model=InvoiceOut)
async def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Accept file upload, extract text (PDF->text or image OCR), parse via AI, save to DB.
    """
    # save file temporarily
    tmp_path = await file_helpers.save_upload_file_tmp(file)

    # extract text
    text = ""
    ext = os.path.splitext(file.filename)[1].lower()
    try:
        if ext == ".pdf":
            text = ocr.extract_text_from_pdf(tmp_path)
        if not text:
            # try image OCR
            text = ocr.extract_text_from_image(tmp_path)
        # attempt reading as plain text for .txt
        if (not text or text.strip() == "") and ext in [".txt", ".md"]:
            with open(tmp_path, "r", encoding="utf-8") as fh:
                text = fh.read()
    except Exception as e:
        file_helpers.cleanup_tmp_file(tmp_path)
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")

    if not text:
        file_helpers.cleanup_tmp_file(tmp_path)
        raise HTTPException(status_code=400, detail="Could not extract text from file.")

    # call the AI extractor
    try:
        parsed = ai_extractor.extract_invoice_data(text)
    except Exception as e:
        file_helpers.cleanup_tmp_file(tmp_path)
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {e}")

    # save invoice and items
    try:
        invoice = Invoice(
            invoice_number = parsed.get("invoice_number"),
            vendor_name = parsed.get("vendor_name"),
            buyer_name = parsed.get("buyer_name"),
            date = parsed.get("date"),
            subtotal = parsed.get("subtotal"),
            tax = parsed.get("tax"),
            total = parsed.get("total"),
            currency = parsed.get("currency"),
            raw_text = parsed.get("raw_text") or text
        )
        db.add(invoice)
        db.flush()  # to get invoice.id

        for it in parsed.get("items") or []:
            item = Item(
                invoice_id = invoice.id,
                name = it.get("name"),
                quantity = it.get("quantity"),
                unit_price = it.get("unit_price"),
                total_price = it.get("total_price")
            )
            db.add(item)

        db.commit()
        db.refresh(invoice)
    except Exception as e:
        db.rollback()
        file_helpers.cleanup_tmp_file(tmp_path)
        raise HTTPException(status_code=500, detail=f"DB save failed: {e}")

    # cleanup
    file_helpers.cleanup_tmp_file(tmp_path)
    return invoice

@router.post("/extract")
async def extract_text_only(payload: dict = Body(...)):
    """
    Accepts {"text": "..."} and returns parsed invoice JSON without saving to DB.
    Useful for UI preview or tests.
    """
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' in request body.")

    try:
        parsed = ai_extractor.extract_invoice_data(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {e}")

    return JSONResponse(content=parsed)

@router.get("/", response_model=List[InvoiceOut])
def list_invoices(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Invoice).offset(skip).limit(limit).all()

@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv
