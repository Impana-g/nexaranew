from fastapi import APIRouter
from pydantic import BaseModel
from services.nlp_service import preprocess_query
from services.sentiment_service import analyze_sentiment
from models.schemas import SentimentResult

router = APIRouter()


class SentimentRequest(BaseModel):
    text: str


@router.post("/sentiment", response_model=SentimentResult)
def get_sentiment(request: SentimentRequest):
    """
    Run only the NLP + sentiment pipeline on any text.
    Useful for testing query sentiment before full analysis.
    """
    nlp = preprocess_query(request.text)
    return analyze_sentiment(nlp)