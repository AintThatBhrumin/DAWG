# backend/run_extraction_on_uploaded.py
import json
from pathlib import Path
from ai_extractor import extract_invoice_auto
from splitter import split_pdf_into_sections

FILES = [
    "C:/Users/Bhrumin/Downloads/ariel.pdf",
    "C:/Users/Bhrumin/Downloads/shampoo.pdf",
]

OUT = "/tmp/invoice_extractor/run_outputs"
Path(OUT).mkdir(parents=True, exist_ok=True)

for f in FILES:
    print("Processing:", f)
    sections = split_pdf_into_sections(f)
    out = {"file": f, "sections": []}
    for sid, text in sections:
        try:
            parsed = extract_invoice_auto(text, is_text=True)
        except Exception as e:
            parsed = {"error": str(e)}
        out["sections"].append({"section_id": sid, "text_snippet": text[:300], "parsed": parsed})
    outfile = Path(OUT) / (Path(f).stem + "_run.json")
    with open(outfile, "w", encoding="utf-8") as fo:
        json.dump(out, fo, ensure_ascii=False, indent=2)
    print("Wrote:", outfile)
print("All done. Check files in", OUT)
