from docx import Document

def extract_text_from_docx(file):
    """Reads a .docx file object and returns full text as a single string."""
    doc = Document(file)
    text = []
    for para in doc.paragraphs:
        if para.text.strip():
            text.append(para.text.strip())
    return "\n".join(text)