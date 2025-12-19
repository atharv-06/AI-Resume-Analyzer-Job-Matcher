# app/utils/pdf_parser.py
import PyPDF2
from io import BytesIO


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text by removing unwanted characters,
    fixing spacing, and normalizing line breaks.
    """
    if not text:
        return ""

    text = text.replace("\x00", "")          # remove null bytes
    text = text.replace("\xa0", " ")         # replace non-breaking spaces
    text = text.replace("\r", " ")           # normalize carriage returns
    text = "\n".join(line.strip() for line in text.split("\n"))  # trim lines
    text = "\n".join([line for line in text.split("\n") if line])  # remove empty lines

    return text.strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file using PyPDF2.
    Works for digital PDFs (non-scanned).
    """

    # Try loading PDF
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
    except Exception:
        return ""

    # Handle encrypted PDFs
    if pdf_reader.is_encrypted:
        try:
            pdf_reader.decrypt("")  # try decrypting with empty password
        except Exception:
            return ""

    extracted_text = ""

    # Extract text page-by-page
    for page in pdf_reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"
        except:
            continue  # skip problematic pages

    return clean_text(extracted_text)
