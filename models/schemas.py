from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class SentimentLabel(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class QueryRequest(BaseModel):
    query: str
    company: Optional[str] = None  # override auto-detection


class NLPResult(BaseModel):
    original_query: str
    cleaned_query: str
    detected_company: Optional[str]
    tokens: List[str]
    keywords: List[str]


class SentimentResult(BaseModel):
    label: SentimentLabel
    score: float  # 0.0 - 1.0
    explanation: str


class BGCheckResult(BaseModel):
    company: str
    ticker: str
    accuracy_score: float  # 0.0 - 1.0
    risk_level: RiskLevel
    red_flags: List[str]
    positive_signals: List[str]
    data_sources: List[str]


class KBEntry(BaseModel):
    company: str
    ticker: str
    summary: str
    last_updated: str
    news_headlines: List[str]
    financial_signals: List[str]
    sentiment_from_kb: SentimentLabel


class AnalysisResponse(BaseModel):
    query: str
    nlp: NLPResult
    sentiment: SentimentResult
    bg_check: BGCheckResult
    kb_snapshot: KBEntry
    final_recommendation: str
    confidence: float
    pipeline_stages: List[str]