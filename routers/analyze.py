from fastapi import APIRouter, HTTPException
from models.schemas import QueryRequest, AnalysisResponse, SentimentLabel, RiskLevel
from services.nlp_service import preprocess_query
from services.sentiment_service import analyze_sentiment
from services.kb_service import fetch_live_kb
from services.bg_check_service import run_bg_check

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_investment_query(request: QueryRequest):
    """
    Full pipeline: query -> NLP -> preprocess -> sentiment -> BG check -> KB lookup -> recommendation
    Supports: Apple (AAPL), IBM, Microsoft (MSFT)
    """
    pipeline_stages = []

    # Stage 1: NLP + Preprocessing
    pipeline_stages.append("NLP Preprocessing")
    nlp = preprocess_query(request.query, company_override=request.company)

    if not nlp.detected_company:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Company not detected in query.",
                "supported_companies": ["Apple", "IBM", "Microsoft"],
                "hint": "Try: 'Should I invest in Apple?' or 'Tell me about IBM stock'"
            }
        )

    # Stage 2: Sentiment Analysis
    pipeline_stages.append("Sentiment Analysis")
    sentiment = analyze_sentiment(nlp)

    # Stage 3: Live KB Update (Tavily)
    pipeline_stages.append("Live KB Fetch (Tavily)")
    kb = await fetch_live_kb(nlp.detected_company)

    # Stage 4: Background Check + Accuracy Scoring
    pipeline_stages.append("Background Check & Accuracy Scoring")
    bg_check = run_bg_check(nlp.detected_company, nlp, kb, sentiment)

    # Stage 5: Final Recommendation
    pipeline_stages.append("Recommendation Engine")
    recommendation = _build_recommendation(bg_check, sentiment, kb)
    confidence = round((bg_check.accuracy_score + sentiment.score) / 2, 3)

    return AnalysisResponse(
        query=request.query,
        nlp=nlp,
        sentiment=sentiment,
        bg_check=bg_check,
        kb_snapshot=kb,
        final_recommendation=recommendation,
        confidence=confidence,
        pipeline_stages=pipeline_stages
    )


def _build_recommendation(bg_check, sentiment, kb) -> str:
    company = bg_check.company
    ticker = bg_check.ticker
    score = bg_check.accuracy_score

    if bg_check.risk_level == RiskLevel.LOW and sentiment.label == SentimentLabel.POSITIVE:
        action = "STRONG BUY"
        rationale = f"{company} ({ticker}) shows strong positive signals across live data and sentiment."
    elif bg_check.risk_level == RiskLevel.LOW:
        action = "BUY"
        rationale = f"{company} ({ticker}) has solid fundamentals with neutral-to-positive market signals."
    elif bg_check.risk_level == RiskLevel.MEDIUM and sentiment.label != SentimentLabel.NEGATIVE:
        action = "HOLD / WATCH"
        rationale = f"{company} ({ticker}) has mixed signals — monitor before committing capital."
    elif bg_check.risk_level == RiskLevel.HIGH or sentiment.label == SentimentLabel.NEGATIVE:
        action = "CAUTION / AVOID"
        rationale = f"{company} ({ticker}) has elevated risk signals. Exercise caution."
    else:
        action = "NEUTRAL"
        rationale = f"Insufficient data to make a strong recommendation for {company} ({ticker})."

    return f"[{action}] {rationale} Accuracy Score: {score:.0%}. Risk: {bg_check.risk_level.value}."