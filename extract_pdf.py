import sys
from pypdf import PdfReader

try:
    reader = PdfReader("C:/DATATHON25/DATALYTIC TRIO.pdf")
    print(f"Number of pages: {len(reader.pages)}")
    full_text = ""
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        print(f"--- PAGE {i+1} ---")
        print(text)
        full_text += text + "\n"
    
except Exception as e:
    print(f"Error reading PDF: {e}")
