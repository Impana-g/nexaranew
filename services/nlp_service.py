# services/nlp_service.py  — spaCy upgraded version

import re
import spacy
from typing import Optional
from core.config import SUPPORTED_COMPANIES, NLP_STOPWORDS
from models.schemas import NLPResult

# Load once at module startup — en_core_web_sm is the small English model
# It knows: POS tags, dependency parse, Named Entities (ORG, PERSON, GPE, etc.)
nlp_model = spacy.load("en_core_web_sm")

# Map spaCy-recognized org names → our company keys
SPACY_ORG_MAP = {
    "apple": "apple",
    "apple inc": "apple",
    "apple inc.": "apple",
    "ibm": "ibm",
    "international business machines": "ibm",
    "microsoft": "microsoft",
    "microsoft corporation": "microsoft",
}


def preprocess_query(query: str, company_override: Optional[str] = None) -> NLPResult:
    """
    Upgraded pipeline:
    query -> normalize -> spaCy NLP -> NER company detect -> keyword extract
    """
    # Step 1: Normalize (same as before)
    cleaned = query.lower().strip()
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Step 2: Run spaCy on the ORIGINAL query (preserves casing for NER)
    doc = nlp_model(query)

    # Step 3: Extract tokens and keywords using spaCy's tokenizer + POS tagger
    # spaCy gives us: token.text, token.pos_, token.is_stop, token.lemma_
    tokens = [token.text.lower() for token in doc]

    # Keep tokens that are: not stopwords, not punctuation, not spaces, length > 1
    # spaCy's is_stop is smarter than our hardcoded set — it's context-aware
    keywords = [
        token.lemma_.lower()          # lemma = base form: "investing" → "invest"
        for token in doc
        if not token.is_stop          # spaCy's built-in stopword list
        and not token.is_punct
        and not token.is_space
        and len(token.text) > 1
        and token.pos_ in            # only keep meaningful word types
            {"NOUN", "PROPN", "VERB", "ADJ"}
    ]

    # Step 4: Detect company using NER
    detected_company = None

    # Override still works the same
    if company_override:
        co = company_override.lower()
        if co in SUPPORTED_COMPANIES:
            detected_company = co
        else:
            for key, meta in SUPPORTED_COMPANIES.items():
                if co in meta["keywords"] or co == meta["ticker"].lower():
                    detected_company = key
                    break

    # spaCy NER — look for ORG entities only
    if not detected_company:
        for ent in doc.ents:
            if ent.label_ == "ORG":           # only organisation entities
                ent_text = ent.text.lower()
                if ent_text in SPACY_ORG_MAP:
                    detected_company = SPACY_ORG_MAP[ent_text]
                    break

    # Fallback: if NER missed it, try keyword match (safety net)
    if not detected_company:
        for key, meta in SUPPORTED_COMPANIES.items():
            for kw in meta["keywords"]:
                if kw in cleaned:
                    detected_company = key
                    break
            if detected_company:
                break

    return NLPResult(
        original_query=query,
        cleaned_query=cleaned,
        detected_company=detected_company,
        tokens=tokens,
        keywords=keywords
    )


def build_search_query(nlp: NLPResult) -> str:
    if nlp.detected_company:
        meta = SUPPORTED_COMPANIES[nlp.detected_company]
        return f"{meta['full_name']} {meta['ticker']} stock investment 2025 financial performance"
    return " ".join(nlp.keywords[:5]) + " stock investment analysis"