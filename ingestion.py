import os
import fitz  # PyMuPDF
from docx import Document

def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    
    # Opening PDF document
    doc = fitz.open(pdf_path)
    
    # Looping through every page and taking hold of the text
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        extracted_text += page.get_text()
        
    return extracted_text

def extract_any_text(file_path):
    """Checks the file type and extracts text accordingly."""
    # Get the file extension (e.g., '.pdf', '.docx', '.txt')
    extension = os.path.splitext(file_path)[1].lower()
    
    if extension == '.pdf':
        return extract_text_from_pdf(file_path)
        
    elif extension == '.docx':
        doc = Document(file_path)
        # Combine all the paragraphs in the Word doc into one giant string
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
    elif extension == '.txt':
        # Standard text files are the easiest!
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    else:
        # Returning an empty string prevents the AI from trying to compare error messages
        return "" 

if __name__ == "__main__":
    # Point the code to the test file (you can test .txt or .docx here too now!)
    test_file_path = "submissions/sample.pdf"
    
    try:
        print(f"Attempting to read: {test_file_path}...")
        # Notice we are calling the new master function here!
        text = extract_any_text(test_file_path)
        
        if text:
            print("\n✅ Extraction successful! Here are the first 300 characters:")
            print("-" * 50)
            print(text[:300]) 
            print("-" * 50)
        else:
            print("\n⚠️ Extraction returned empty text. (Unsupported file or empty document)")
        
    except Exception as e:
        print(f"\n❌ Oops, ran into an error: {e}")