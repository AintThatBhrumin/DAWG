import json
from ai_extractor import call_text_llm, PROMPT_TEMPLATE
from utils.pdf_reader import pdf_to_text

# UPDATE THIS PATH —
PDF_PATH = r"C:\Users\Bhrumin\Downloads\shampoo.pdf"

text = pdf_to_text(PDF_PATH)
prompt = PROMPT_TEMPLATE.format(invoice_text=text)

print("=== PROMPT SENT TO MODEL ===")
print(prompt)
print("\n=== RAW OUTPUT ===")
result = call_text_llm(prompt)
print("\n=== PARSED OUTPUT ===")
print(json.dumps(result, indent=2))
