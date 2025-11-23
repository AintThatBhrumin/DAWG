# backend/annotate_helper.py
import json
import os
from pathlib import Path

DATA_DIR = os.environ.get("TMP_DIR", "/tmp/invoice_extractor")
GOLD_DIR = os.path.join(DATA_DIR, "gold")
os.makedirs(GOLD_DIR, exist_ok=True)

def export_for_annotation(jsonl_path: str):
    with open(jsonl_path, "r", encoding="utf-8") as f:
        lines = [json.loads(l) for l in f if l.strip()]
    annot_path = os.path.join(GOLD_DIR, Path(jsonl_path).name)
    with open(annot_path, "w", encoding="utf-8") as fo:
        # write pretty JSON for manual editing (one JSON object per line or as array)
        json.dump(lines, fo, ensure_ascii=False, indent=2)
    print("Exported for annotation:", annot_path)
    return annot_path

def import_corrected(annot_path: str):
    with open(annot_path, "r", encoding="utf-8") as f:
        corrected = json.load(f)
    # Save per-line JSONL of corrected gold
    out = os.path.join(GOLD_DIR, "corrected_gold.jsonl")
    with open(out, "a", encoding="utf-8") as fo:
        for rec in corrected:
            fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("Imported corrected gold to:", out)
    return out
