import pdfplumber
from docx import Document

def extract_from_pdf(file_path: str) -> list[dict]:
    pages = []

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()

            if text and text.strip():
                pages.append({
                    "text": text,
                    "page": i + 1
                })

    return pages