from models.schemas import SentimentResult, SentimentLabel, NLPResult

# Removed "invest", "buy", "sell" — intent words, not sentiment
POSITIVE_LEXICON = {
    "growth", "profit", "strong", "good", "great", "excellent",
    "rise", "surge", "beat", "record", "positive", "bullish", "opportunity",
    "gain", "increase", "expand", "innovative", "leading", "dividend", "upgrade",
    "exceed", "outperform", "advance", "recovery", "rally", "robust", "solid",
    "momentum", "breakthrough", "efficient", "confidence", "optimistic"
}

NEGATIVE_LEXICON = {
    "loss", "weak", "bad", "poor", "fall", "drop", "miss", "risk",
    "decline", "negative", "bearish", "concern", "cut", "downgrade", "fraud",
    "lawsuit", "debt", "bankrupt", "crisis", "volatility", "uncertainty",
    "underperform", "disappoint", "slump", "warning", "trouble", "fail",
    "collapse", "fear", "panic", "recession", "layoff", "deficit"
}

INTENSIFIERS = {"very", "extremely", "highly", "significantly", "strongly", "major", "particularly"}
NEGATORS = {"not", "no", "never", "don't", "doesn't", "isn't", "aren't", "won't", "barely", "hardly"}


def analyze_sentiment(nlp_result: NLPResult) -> SentimentResult:
    tokens = nlp_result.tokens
    keywords = set(nlp_result.keywords)

    pos_score = 0.0
    neg_score = 0.0
    intensity_multiplier = 1.0
    negate = False
    negate_window = 0

    for token in tokens:
        if token in NEGATORS:
            negate = True
            negate_window = 0
            continue

        if token in INTENSIFIERS:
            intensity_multiplier *= 1.5
            continue

        # Negation expires after 2 non-lexicon tokens
        if negate:
            negate_window += 1
            if negate_window > 2:
                negate = False

        weight = intensity_multiplier * (1.5 if token in keywords else 1.0)

        if token in POSITIVE_LEXICON:
            if negate:
                neg_score += weight
            else:
                pos_score += weight
            negate = False
            intensity_multiplier = 1.0

        elif token in NEGATIVE_LEXICON:
            if negate:
                pos_score += weight
            else:
                neg_score += weight
            negate = False
            intensity_multiplier = 1.0

    total = pos_score + neg_score
    if total == 0:
        return SentimentResult(
            label=SentimentLabel.NEUTRAL,
            score=0.5,
            explanation="Query is neutral/informational — no strong sentiment signals detected."
        )

    raw_pos = pos_score / total

    if raw_pos > 0.6:
        label = SentimentLabel.POSITIVE
        score = round(0.5 + (raw_pos - 0.5) * 0.8, 3)
        explanation = f"Positive signals detected (pos={pos_score:.1f}, neg={neg_score:.1f})."
    elif raw_pos < 0.4:
        label = SentimentLabel.NEGATIVE
        score = round(0.5 + (0.5 - raw_pos) * 0.8, 3)
        explanation = f"Negative/risk signals detected (pos={pos_score:.1f}, neg={neg_score:.1f})."
    else:
        label = SentimentLabel.NEUTRAL
        score = 0.5
        explanation = f"Mixed signals detected (pos={pos_score:.1f}, neg={neg_score:.1f})."

    return SentimentResult(label=label, score=score, explanation=explanation)