from datetime import datetime
from models.schemas import BGCheckResult, KBEntry, NLPResult, SentimentResult, RiskLevel, SentimentLabel
from core.config import SUPPORTED_COMPANIES


def run_bg_check(
    company_key: str,
    nlp: NLPResult,
    kb: KBEntry,
    sentiment: SentimentResult
) -> BGCheckResult:
    meta = SUPPORTED_COMPANIES.get(company_key, {})
    ticker = meta.get("ticker", "UNKNOWN")

    red_flags = []
    positive_signals = []
    score_components = []

    # --- Check 1: KB data freshness (replaced dead code) ---
    try:
        age_seconds = (datetime.utcnow() - datetime.fromisoformat(kb.last_updated)).total_seconds()
        if age_seconds < 300:
            positive_signals.append("KB data is fresh (under 5 min old).")
            score_components.append(0.85)
        else:
            red_flags.append("KB data may be stale — fetched over 5 min ago.")
            score_components.append(0.55)
    except Exception:
        score_components.append(0.6)

    # --- Check 2: Live KB sentiment ---
    if kb.sentiment_from_kb == SentimentLabel.POSITIVE:
        positive_signals.append("Live news sentiment is positive.")
        score_components.append(0.9)
    elif kb.sentiment_from_kb == SentimentLabel.NEGATIVE:
        red_flags.append("Live news sentiment is negative — market caution advised.")
        score_components.append(0.35)
    else:
        score_components.append(0.6)

    # --- Check 3: Financial signals present ---
    if kb.financial_signals:
        positive_signals.append(f"{len(kb.financial_signals)} financial signals found.")
        score_components.append(0.8)
    else:
        red_flags.append("No financial signals found in KB — limited data.")
        score_components.append(0.4)

    # --- Check 4: User query sentiment (lower weight — intent not quality) ---
    if sentiment.label == SentimentLabel.POSITIVE:
        positive_signals.append("User query has positive investment intent.")
        score_components.append(0.6)      # Fix: was 0.75, reduced
    elif sentiment.label == SentimentLabel.NEGATIVE:
        red_flags.append("User query contains negative/risk language.")
        score_components.append(0.4)
    else:
        score_components.append(0.5)      # Fix: neutral gets 0.5 not 0.6

    # --- Check 5: News headline count ---
    if len(kb.news_headlines) >= 3:
        positive_signals.append(f"{len(kb.news_headlines)} recent headlines found.")
        score_components.append(0.8)
    else:
        red_flags.append("Fewer than 3 recent news items — coverage is sparse.")
        score_components.append(0.45)

    accuracy = round(sum(score_components) / len(score_components), 3)

    # Fix: AND logic so both conditions must hold for LOW
    if accuracy >= 0.75 and len(red_flags) == 0:
        risk = RiskLevel.LOW
    elif accuracy >= 0.55 and len(red_flags) <= 1:   # Fix: AND not OR
        risk = RiskLevel.MEDIUM
    else:
        risk = RiskLevel.HIGH

    data_sources = ["Tavily Live Search", "Pre-trained Tech Company KB", "Lexicon Sentiment Engine"]

    return BGCheckResult(
        company=kb.company,
        ticker=ticker,
        accuracy_score=accuracy,
        risk_level=risk,
        red_flags=red_flags,
        positive_signals=positive_signals,
        data_sources=data_sources
    )