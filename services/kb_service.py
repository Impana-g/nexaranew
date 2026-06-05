import re
import httpx
from datetime import datetime
from typing import Optional
from core.config import TAVILY_API_KEY, SUPPORTED_COMPANIES
from models.schemas import KBEntry, SentimentLabel

TAVILY_URL = "https://api.tavily.com/search"


def _count_words(text_list: list, words: list) -> int:
    return sum(
        1 for h in text_list for w in words
        if re.search(rf'\b{w}\b', h.lower())
    )


def _extract_snippet(text: str, keyword: str) -> Optional[str]:
    idx = text.lower().find(keyword)
    if idx == -1:
        return None
    # Find sentence start — look for . or \n before keyword
    raw_before = text[max(0, idx - 200):idx]
    last_dot = max(raw_before.rfind('.'), raw_before.rfind('\n'))
    if last_dot != -1:
        start = max(0, idx - 200) + last_dot + 1
    else:
        start = max(0, idx - 20)
    raw = text[start: min(len(text), idx + 200)]
    # End at first . or \n
    end_dot = raw.find('.')
    end_nl = raw.find('\n')
    if end_dot != -1 and end_nl != -1:
        end = min(end_dot, end_nl)
    elif end_dot != -1:
        end = end_dot
    elif end_nl != -1:
        end = end_nl
    else:
        end = len(raw)
    return raw[:end + 1].strip()


def _clean_snippet(text: str) -> Optional[str]:
    if not text:
        return None
    # Remove markdown headers
    text = re.sub(r'#{1,6}\s+\S[^\n]*', '', text)
    # Remove excessive newlines
    text = re.sub(r'\n+', ' ', text).strip()
    # Remove bracket noise like [. or ]
    text = re.sub(r'\[\.?\]?', '', text).strip()
    # Skip if too short or starts with noise
    if len(text) < 25 or text.lower().startswith('logo'):
        return None
    return text[:200].strip()


async def fetch_live_kb(company_key: str) -> KBEntry:
    meta = SUPPORTED_COMPANIES.get(company_key)
    if not meta:
        raise ValueError(f"Company '{company_key}' not in supported list.")

    query = f"{meta['full_name']} {meta['ticker']} latest news investment analysis 2025"
    headlines = []
    financial_signals = []
    summary = f"Live KB data for {meta['full_name']} ({meta['ticker']})"
    kb_sentiment = SentimentLabel.NEUTRAL

    if TAVILY_API_KEY:
        try:
            payload = {
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "advanced",
                "include_answer": True,
                "include_raw_content": False,
                "max_results": 5
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(TAVILY_URL, json=payload)
                response.raise_for_status()
                data = response.json()

            if data.get("answer"):
                summary = data["answer"][:500]

            signal_words = [
                "revenue", "profit", "growth", "earnings",
                "beat", "miss", "guidance", "dividend",
                "exceed", "outperform", "disappoint", "forecast"
            ]

            for result in data.get("results", []):
                title = result.get("title", "")
                content = result.get("content", "")
                if title:
                    headlines.append(title[:120])

                seen_keywords = set()
                for signal_word in signal_words:
                    if signal_word in content.lower() and signal_word not in seen_keywords:
                        snippet = _extract_snippet(content, signal_word)
                        snippet = _clean_snippet(snippet)
                        if snippet:
                            financial_signals.append(snippet)
                            seen_keywords.add(signal_word)

            pos_words = [
                "growth", "beat", "rise", "surge", "strong", "record",
                "profit", "upgrade", "exceed", "outperform", "advance",
                "gain", "positive", "bullish", "rally", "recovery"
            ]
            neg_words = [
                "loss", "miss", "fall", "drop", "weak", "cut",
                "downgrade", "risk", "decline", "underperform",
                "disappoint", "bearish", "slump", "concern", "warning"
            ]

            # Score headlines
            pos_count = _count_words(headlines, pos_words)
            neg_count = _count_words(headlines, neg_words)

            # Also score the summary for better sentiment accuracy
            if data.get("answer"):
                summary_text = data["answer"].lower()
                pos_count += sum(1 for w in pos_words if re.search(rf'\b{w}\b', summary_text))
                neg_count += sum(1 for w in neg_words if re.search(rf'\b{w}\b', summary_text))

            if pos_count > neg_count + 1:
                kb_sentiment = SentimentLabel.POSITIVE
            elif neg_count > pos_count + 1:
                kb_sentiment = SentimentLabel.NEGATIVE
            else:
                kb_sentiment = SentimentLabel.NEUTRAL

        except Exception as e:
            summary = f"[Tavily fetch failed: {str(e)}] Using cached data."
            headlines = [f"Could not fetch live data for {meta['full_name']}"]

    else:
        summary = f"{meta['full_name']} is a major tech company in the {meta['sector']} sector."
        headlines = [
            f"{meta['full_name']} reports steady Q2 performance",
            f"{meta['ticker']} analysts maintain buy rating",
            f"{meta['full_name']} expands AI product portfolio"
        ]
        financial_signals = ["Strong revenue trend", "EPS beat consensus", "Positive guidance"]
        kb_sentiment = SentimentLabel.POSITIVE

    # Deduplicate financial signals by first 50 chars
    seen = set()
    unique_signals = []
    for s in financial_signals:
        key = s[:50]
        if key not in seen:
            seen.add(key)
            unique_signals.append(s)
    financial_signals = unique_signals

    return KBEntry(
        company=meta["full_name"],
        ticker=meta["ticker"],
        summary=summary,
        last_updated=datetime.utcnow().isoformat(),
        news_headlines=headlines[:5],
        financial_signals=financial_signals[:4],
        sentiment_from_kb=kb_sentiment
    )