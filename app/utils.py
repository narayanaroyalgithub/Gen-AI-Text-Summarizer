import hashlib
import json

def doc_to_text(file_bytes, filename):
    # Simple heuristic: assume text files; extend with pdf -> text using tika/pdfplumber if needed
    try:
        return file_bytes.decode("utf-8")
    except Exception:
        return ""  # extend parsing for PDFs in production

def make_cache_key(text):
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"summary:{h}"
