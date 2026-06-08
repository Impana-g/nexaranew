from services.pdf_service import extract_pdf_text

pdf_file = "sample.pdf"   # replace with your PDF name

text = extract_pdf_text(pdf_file)

print(text[:1000])