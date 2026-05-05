"""
Pulls the raw contract text, handles plain text, PDF, and Word
"""

import io

from pypdf import PdfReader
from docx import Document


def read_txt(file_bytes):
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1", errors="ignore")


def read_pdf(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))

    page_texts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        page_texts.append(page_text)

    return "\n\n".join(page_texts)


def read_docx(file_bytes):
    doc = Document(io.BytesIO(file_bytes))

    # drop empty paragraphs
    paragraphs = []
    for p in doc.paragraphs:
        if p.text.strip():
            paragraphs.append(p.text)

    return "\n\n".join(paragraphs)


def extract_text(filename, file_bytes):
    lower_name = filename.lower()

    if lower_name.endswith(".txt"):
        return read_txt(file_bytes)
    if lower_name.endswith(".pdf"):
        return read_pdf(file_bytes)
    if lower_name.endswith(".docx"):
        return read_docx(file_bytes)

    raise ValueError("Unsupported file type. Please upload a .txt, .pdf, or .docx file.")
