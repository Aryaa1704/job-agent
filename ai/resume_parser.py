import fitz  # pymupdf
import docx
import re

def extract_from_pdf(file_bytes: bytes) -> str:
    """PDF se text extract karo"""
    text = ""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text()
    except Exception as e:
        text = f"PDF read error: {e}"
    return text.strip()

def extract_from_docx(file_bytes: bytes) -> str:
    """DOCX se text extract karo"""
    import io
    text = ""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        text = f"DOCX read error: {e}"
    return text.strip()

def extract_resume_text(uploaded_file) -> str:
    """
    Streamlit uploaded file se text nikalo
    Supports: PDF, DOCX, TXT
    """
    if uploaded_file is None:
        return ""
    
    file_bytes = uploaded_file.read()
    name = uploaded_file.name.lower()
    
    if name.endswith(".pdf"):
        return extract_from_pdf(file_bytes)
    elif name.endswith(".docx") or name.endswith(".doc"):
        return extract_from_docx(file_bytes)
    elif name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        # Try as text
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except:
            return "File format support nahi hai"
