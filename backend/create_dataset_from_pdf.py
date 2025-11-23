# backend/create_dataset_from_pdf.py
import os
import json
from splitter import split_pdf_into_sections
from ai_extractor import extract_invoice_auto

OUT_DIR = os.environ.get("TMP_DIR", "/tmp/invoice_extractor")
os.makedirs(OUT_DIR, exist_ok=True)

def process_pdf(pdf_path: str, output_prefix: str = None):
    base = output_prefix or os.path.basename(pdf_path).rsplit(".",1)[0]
    sections = split_pdf_into_sections(pdf_path)
    results = []
    for sid, text in sections:
        try:
            # use text-mode extraction to avoid re-OCRing; pass is_text=True
            parsed = extract_invoice_auto(text, is_text=True)
        except Exception as e:
            parsed = {"error": str(e)}
        rec = {
            "file": pdf_path,
            "section_id": sid,
            "text": text,
            "model_output": parsed
        }
        results.append(rec)
        # append to JSONL
        out_file = os.path.join(OUT_DIR, f"{base}_dataset.jsonl")
        with open(out_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"Wrote section {sid} → {out_file}")
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python create_dataset_from_pdf.py path/to/file.pdf")
        raise SystemExit(1)
    path = sys.argv[1]
    process_pdf(path)
    print("Done.")
