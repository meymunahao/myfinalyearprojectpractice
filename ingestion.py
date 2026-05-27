import fitz  # This is PyMuPDF!

def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    
    # Opening PDF document
    doc = fitz.open(pdf_path)
    
    # Looping through every page and taking hold of the text
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        extracted_text += page.get_text()
        
    return extracted_text

if __name__ == "__main__":
    # Point the code to the test PDF you just saved
    test_pdf_path = "submissions/sample.pdf"
    
    try:
        print(f"Attempting to read: {test_pdf_path}...")
        text = extract_text_from_pdf(test_pdf_path)
        
        print("\n✅ Extraction successful! Here are the first 300 characters:")
        print("-" * 50)
        print(text[:300]) 
        print("-" * 50)
        
    except Exception as e:
        print(f"\n❌ Oops, ran into an error: {e}")