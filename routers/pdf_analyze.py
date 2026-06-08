from fastapi import APIRouter, UploadFile, File
from services.pdf_service import extract_pdf_text
import tempfile
from services.rag_service import build_vector_store
router = APIRouter()


@router.post("/analyze-pdf")
async def analyze_pdf(file: UploadFile = File(...)):

    # Save uploaded PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp.write(await file.read())
        pdf_path = temp.name

    # Extract text
    text = extract_pdf_text(pdf_path)
    build_vector_store(text)

    text_lower = text.lower()

    # Check if this is actually a financial document
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

    # If not financial, stop here
    if financial_count < 3:
        return {
            "document_type": "Non-Financial Document",
            "recommendation": "N/A",
            "message": "Uploaded PDF is not a financial report and cannot be used for investment recommendation.",
            "preview": text[:1000]
        }

    # Financial analysis
    positive_words = [
        "growth",
        "profit",
        "increase",
        "strong",
        "revenue",
        "expansion",
        "innovation"
    ]

    negative_words = [
        "loss",
        "risk",
        "decline",
        "debt",
        "drop",
        "weak",
        "lawsuit"
    ]

    pos_count = sum(
        text_lower.count(word)
        for word in positive_words
    )

    neg_count = sum(
        text_lower.count(word)
        for word in negative_words
    )

    if pos_count > neg_count:
        recommendation = "BUY"
        risk = "LOW"

    elif neg_count > pos_count:
        recommendation = "AVOID"
        risk = "HIGH"

    else:
        recommendation = "HOLD"
        risk = "MEDIUM"

    return {
        "document_type": "Financial Report",
        "recommendation": recommendation,
        "risk": risk,
        "positive_signals": pos_count,
        "negative_signals": neg_count,
        "preview": text[:1000]
    }