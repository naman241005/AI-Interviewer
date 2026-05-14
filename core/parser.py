import io
import PyPDF2
import pytesseract
from PIL import Image
import docx

# Update this path if Tesseract is installed elsewhere on your machine
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(file) -> str:
    """
    Extract plain text from uploaded resume files.
    Supports: TXT, PDF (text + scanned), DOCX, PNG, JPG/JPEG.
    FIX: app.py was using raw .decode() instead of this parser — images/PDFs failed silently.
    """
    if file is None:
        return ""

    file_type = file.type
    file.seek(0)

    # ── TXT ───────────────────────────────────────────────
    if file_type == "text/plain":
        try:
            return file.read().decode("utf-8")
        except UnicodeDecodeError:
            file.seek(0)
            return file.read().decode("latin-1", errors="ignore")

    # ── PDF ───────────────────────────────────────────────
    elif file_type == "application/pdf":
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""

            # Scanned PDF fallback → OCR
            if not text.strip():
                file.seek(0)
                images = _pdf_to_images(file)
                for img in images:
                    text += pytesseract.image_to_string(img)
        except Exception as e:
            return f"PDF Error: {e}"
        return text

    # ── DOCX ──────────────────────────────────────────────
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            doc = docx.Document(file)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            return f"DOCX Error: {e}"

    # ── IMAGE ─────────────────────────────────────────────
    elif file_type in ["image/png", "image/jpeg"]:
        try:
            image = Image.open(file).convert("RGB")
            return pytesseract.image_to_string(image)
        except Exception as e:
            return f"Image OCR Error: {e}"

    return ""


def _pdf_to_images(file):
    """Convert PDF bytes to PIL images for OCR."""
    from pdf2image import convert_from_bytes
    return convert_from_bytes(file.read())
