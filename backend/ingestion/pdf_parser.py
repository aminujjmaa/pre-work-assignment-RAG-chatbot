import fitz  # PyMuPDF
import re
import io
from pathlib import Path
from typing import List, Dict, Any

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


def extract_text_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract text from all pages of a PDF.
    Falls back to OCR for pages with sparse native text.
    Returns list of {page_num, text, is_ocr} dicts.
    """
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        is_ocr = False

        # OCR fallback for pages with very little native text
        if len(text.strip()) < 80 and OCR_AVAILABLE:
            try:
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text = pytesseract.image_to_string(img, config="--psm 3")
                is_ocr = True
            except Exception:
                pass

        cleaned = _clean_text(text)
        if cleaned:
            pages.append({
                "page_num": page_num + 1,
                "text": cleaned,
                "is_ocr": is_ocr,
            })

    doc.close()
    return pages


def _clean_text(text: str) -> str:
    """Normalize whitespace, drop lone page-number lines."""
    # Remove lines that are just numbers (page numbers)
    text = re.sub(r"(?m)^\s*\d{1,4}\s*$", "", text)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()
