"""
DAWG/backend/app/utils/file_helpers.py

Helpers to save uploaded files to a temp folder and cleanup.
"""
import os
import uuid
from fastapi import UploadFile

TMP_DIR = os.getenv("TMP_DIR", "/tmp/invoice_extractor")
os.makedirs(TMP_DIR, exist_ok=True)

async def save_upload_file_tmp(upload_file: UploadFile) -> str:
    """
    Save FastAPI UploadFile to a temp path and return that path.
    """
    ext = os.path.splitext(upload_file.filename)[1] or ""
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(TMP_DIR, filename)
    content = await upload_file.read()
    with open(path, "wb") as f:
        f.write(content)
    return path

def cleanup_tmp_file(path: str):
    try:
        os.remove(path)
    except Exception:
        pass
