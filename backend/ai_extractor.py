# backend/ai_extractor.py
"""
Unified extractor:
- If provided a file path (pdf/image/text file): auto-detect pipeline.
- If provided an actual text string, use text parsing.
- Uses local LM Studio by default (LMSTUDIO_URL) or OpenRouter if OPENROUTER_API_KEY set.

Exported function:
    extract_invoice_auto(path_or_text: str, is_text=False) -> dict
"""

import os
import json
import re
import tempfile
import base64
import requests
from typing import List

from dotenv import load_dotenv
load_dotenv()

# Environment config
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://api.openrouter.ai/v1/chat/completions")

LMSTUDIO_CHAT_URL = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1/chat/completions")
LMSTUDIO_VISION_URL = os.getenv("LMSTUDIO_VISION_URL", LMSTUDIO_CHAT_URL)

TEXT_MODEL = os.getenv("TEXT_MODEL", "qwen/qwen3-vl-4b")  # used for text parsing if desired
VISION_MODEL = os.getenv("VISION_MODEL", os.getenv("LMSTUDIO_MODEL", "qwen/qwen3-vl-4b"))

# local utility imports (safe to import here)
from utils.pdf_reader import pdf_has_text, pdf_to_text, pdf_to_images
from utils.ocr_reader import image_to_text, multiple_images_to_text

# Prompt template (strict JSON output)
PROMPT_TEMPLATE = """
You are an invoice parsing expert. Extract fields and return ONLY valid JSON (no explanation).

Schema:
{{
  "invoice_number": string or null,
  "date": string or null,
  "vendor_name": string or null,
  "buyer_name": string or null,
  "gst_number": string or null,
  "currency": string or null,
  "subtotal": number or null,
  "tax": number or null,
  "total": number or null,
  "items": [
    {{
      "name": string or null,
      "quantity": number or null,
      "unit_price": number or null,
      "total_price": number or null
    }}
  ],
  "raw_text": string
}}

Invoice text:
\"\"\"{invoice_text}\"\"\"
"""

# ----------------------
# Helpers for LLM calls
# ----------------------
def _clean_model_json_text(raw: str) -> str:
    """
    Extracts and repairs JSON from messy model output.
    Handles:
    - missing closing braces
    - trailing commas
    - single quotes
    - markdown code blocks
    """
    if raw is None:
        raise ValueError("Model returned empty response")

    raw = raw.strip()

    # Remove markdown fences ```json ... ```
    raw = re.sub(r"```json", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```", "", raw)

    # Extract largest JSON-like structure
    m = re.search(r"\{[\s\S]*\}", raw)
    if m:
        raw = m.group(0)

    # Fix common JSON issues
    raw = raw.replace("'", "\"")
    raw = re.sub(r",\s*}", "}", raw)
    raw = re.sub(r",\s*]", "]", raw)

    # Fix unclosed braces/brackets
    open_braces = raw.count("{")
    close_braces = raw.count("}")
    if close_braces < open_braces:
        raw += "}" * (open_braces - close_braces)

    open_brackets = raw.count("[")
    close_brackets = raw.count("]")
    if close_brackets < open_brackets:
        raw += "]" * (open_brackets - close_brackets)

    return raw

def _post_chat(payload: dict, url: str, headers: dict = None, timeout: int = 300) -> dict:
    headers = headers or {"Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()

def call_text_llm(prompt_text: str, model: str = TEXT_MODEL) -> dict:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": "You are an invoice parsing assistant. Return ONLY JSON."}
                ]
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text}
                ]
            }
        ],
        "temperature": 0,
        "max_tokens": 2000
    }

    # Send request
    if OPENROUTER_API_KEY:
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        resp = _post_chat(payload, OPENROUTER_URL, headers=headers)
    else:
        resp = _post_chat(payload, LMSTUDIO_CHAT_URL)

    msg = resp.get("choices", [{}])[0].get("message", {})
    raw = msg.get("content") or resp.get("choices", [{}])[0].get("text")

    if raw is None:
        raise RuntimeError(f"Model returned empty content. Full response:\n{json.dumps(resp, indent=2)}")

    # 1️⃣ Try direct JSON (best case)
    try:
        return json.loads(raw)
    except:
        pass

    # 2️⃣ Remove whitespace-only junk around JSON
    stripped = raw.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        try:
            return json.loads(stripped)
        except:
            pass

    # 3️⃣ Fallback cleaning
    cleaned = _clean_model_json_text(raw)

    try:
        return json.loads(cleaned)
    except:
        cleaned2 = cleaned.replace("'", "\"")
        cleaned2 = re.sub(r",\s*}", "}", cleaned2)
        cleaned2 = re.sub(r",\s*]", "]", cleaned2)
        return json.loads(cleaned2)


def call_vlm_image(image_path: str, model: str = VISION_MODEL) -> dict:
    """
    Send a single image to the local LM Studio VLM endpoint.
    Uses base64-encoded image in the chat messages payload (LM Studio-compatible).
    """
    with open(image_path, "rb") as f:
        b = f.read()
    b64 = base64.b64encode(b).decode()

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Extract invoice fields and return ONLY JSON."},
            {"role": "user", "content": [
                {"type": "input_image", "image_url": f"data:image/png;base64,{b64}"},
                {"type": "text", "text": "Return structured JSON following the schema."}
            ]}
        ],
        "temperature": 0,
        "max_tokens": 2000
    }

    resp = _post_chat(payload, LMSTUDIO_VISION_URL)
    raw = (resp.get("choices", [{}])[0].get("message") or {}).get("content")
    cleaned = _clean_model_json_text(raw)
    return json.loads(cleaned)


# -----------------------
# Public unified entry
# -----------------------
def extract_invoice_auto(path_or_text: str, is_text: bool = False) -> dict:
    """
    If is_text=True -> treat path_or_text as raw text string (call text parser).
    Otherwise treat path_or_text as file path:
      - pdf -> try selectable text, else convert pages to images and OCR, then parse text
      - image -> call VLM image pipeline (direct image -> JSON)
      - text file -> read & parse
    Returns parsed JSON dict.
    """

    # If caller explicitly passes text
    if is_text:
        prompt = PROMPT_TEMPLATE.format(invoice_text=path_or_text)
        parsed = call_text_llm(prompt)
        parsed.setdefault("raw_text", path_or_text)
        parsed.setdefault("items", parsed.get("items") or [])
        return parsed

    fp = str(path_or_text)
    lower = fp.lower()

    # PDF path
    if lower.endswith(".pdf"):
        if pdf_has_text(fp):
            text = pdf_to_text(fp)
        else:
            # scanned -> convert to images then OCR with pytesseract then parse text
            images = pdf_to_images(fp)
            text = multiple_images_to_text(images)
        if not text or not text.strip():
            raise RuntimeError("No text could be extracted from PDF.")
        prompt = PROMPT_TEMPLATE.format(invoice_text=text)
        parsed = call_text_llm(prompt)
        parsed.setdefault("raw_text", text)
        parsed.setdefault("items", parsed.get("items") or [])
        return parsed

    # Image path
    if lower.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp")):
        return call_vlm_image(fp)

    # Otherwise treat as text file
    try:
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception:
        raise RuntimeError("Unsupported file type or failed to read file.")

    if not text.strip():
        raise RuntimeError("No text found in file.")
    prompt = PROMPT_TEMPLATE.format(invoice_text=text)
    parsed = call_text_llm(prompt)
    parsed.setdefault("raw_text", text)
    parsed.setdefault("items", parsed.get("items") or [])
    return parsed


def repair_broken_json(text):
    """
    Attempts to auto-fix common JSON issues:
    - missing commas
    - trailing commas
    - unquoted keys
    - unfinished keys like "invoice_number"
    """
    # Fix trailing commas
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)

    # Quote unquoted keys
    text = re.sub(r"(\w+):", r'"\1":', text)

    # Ensure all keys have values
    text = re.sub(r'"\w+"\s*:\s*(?=})', '""', text)

    # If JSON ends abruptly, close brackets
    if text.count("{") > text.count("}"):
        text += "}" * (text.count("{") - text.count("}"))

    if text.count("[") > text.count("]"):
        text += "]" * (text.count("[") - text.count("]"))

    return text
