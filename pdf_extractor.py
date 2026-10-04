"""
pdf_extractor.py
-----------------
Extracts readable text from an uploaded policy PDF.

Tries pdfplumber first (better layout handling), and falls back to
PyPDF2 if pdfplumber fails for a particular file. If neither can read
the PDF, raises PDFExtractionError so app.py can show a simple error
message to the user.
"""

import re

import pdfplumber
from PyPDF2 import PdfReader


class PDFExtractionError(Exception):
    """Raised when text cannot be extracted from the uploaded PDF."""
    pass


def _extract_with_pdfplumber(file_stream):
    text_parts = []
    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
            
            # Also extract tables to ensure tabular data is captured as clear sentences
            for table in page.extract_tables():
                for row in table:
                    # Filter out empty cells and replace newlines within cells
                    clean_row = [str(cell).strip().replace('\n', ' ') for cell in row if cell]
                    if len(clean_row) > 1:
                        # Append the row as a hyphen-separated sentence
                        text_parts.append(" - ".join(clean_row) + ".")
                        
    return "\n".join(text_parts).strip()


def _extract_with_pypdf2(file_stream):
    file_stream.seek(0)
    reader = PdfReader(file_stream)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def _sanitize_extracted_text(text):
    text = text.replace('(cid:127)', '')
    # Fix corrupted Rupee sign: 'n' or '■' before a digit
    text = re.sub(r'(?<![a-zA-Z])[n■](\d[\d,]+)', r'Rs \1', text)
    # Normalise actual ₹ to Rs for consistent display without breaking sent_tokenize
    text = text.replace('₹', 'Rs ')
    # Clean up spacing around Rs. ("Rs.8000" -> "Rs 8000")
    text = re.sub(r'Rs\.(\s*)', 'Rs ', text)
    return text


def extract_text_from_pdf(file_stream):
    """
    Extract text from a PDF file.

    Args:
        file_stream: a file-like object (e.g. Flask's request.files['pdf'])

    Returns:
        str: extracted text

    Raises:
        PDFExtractionError: if no readable text could be found
    """
    text = ""

    try:
        file_stream.seek(0)
        text = _extract_with_pdfplumber(file_stream)
    except Exception:
        text = ""

    if not text:
        try:
            text = _extract_with_pypdf2(file_stream)
        except Exception:
            text = ""

    text = _sanitize_extracted_text(text)

    if not text or len(text.strip()) < 20:
        raise PDFExtractionError(
            "We could not read this PDF. It may be a scanned image "
            "without selectable text, or the file may be corrupted. "
            "Please try another file or paste the policy text instead."
        )

    return text
