from fastapi import APIRouter, UploadFile, File
from services.pdf_service import extract_pdf_text
from services.rag_service import (
    build_vector_store,
    analyze_financial_document
)
import tempfile
import time

router = APIRouter()


@router.post("/analyze-pdf")
async def analyze_pdf(file: UploadFile = File(...)):

    print("STEP 1: PDF uploaded")

    # Save uploaded PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp.write(await file.read())
        pdf_path = temp.name

    # Extract text
    start = time.time()

    text = extract_pdf_text(pdf_path)

    print("STEP 2: Text extracted")
    print("Text length:", len(text))
    print("Extraction Time:", round(time.time() - start, 2), "seconds")

    # Limit huge PDFs for faster processing
    text = text[:50000]

    # Check if document is financial
    text_lower = text.lower()

    financial_keywords = [
        "revenue",
        "profit",
        "earnings",
        "cash flow",
        "dividend",
        "balance sheet",
        "income statement",
        "guidance"
    ]

    financial_count = sum(
        text_lower.count(word)
        for word in financial_keywords
    )

    if financial_count < 3:
        return {
            "document_type": "Non-Financial Document",
            "recommendation": "N/A",
            "message": "Uploaded PDF is not a financial report and cannot be used for investment recommendation.",
            "preview": text[:1000]
        }

    # Claude Analysis
    print("STEP 3: Claude analysis started")

    analysis = analyze_financial_document(text)

    print("STEP 4: Claude analysis completed")

    # Build FAISS for RAG
    start = time.time()

    build_vector_store(text)

    print("STEP 5: FAISS index built")
    print("FAISS Time:", round(time.time() - start, 2), "seconds")

    return {
        "document_type": "Financial Report",
        "ai_analysis": analysis,
        "preview": text[:1000]
    }