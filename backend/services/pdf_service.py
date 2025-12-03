import io 
from pypdf import PdfReader

def extract_text_from_pdf(file_content: bytes) -> str: 
    """Reads raw files from pdf and extracts the text string"""
    try:
        pdf_content = PdfReader(io.BytesIO(file_content))
        extracted_text = ""
        for page in pdf_content.pages: 
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        return extracted_text.strip() 
    except Exception as e: 
        print(f"Error reading pdf: {e}")
        return "" 
