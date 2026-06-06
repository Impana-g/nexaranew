import os
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")


# Supported tech companies for training/KB
SUPPORTED_COMPANIES = {
    "apple": {
        "ticker": "AAPL",
        "full_name": "Apple Inc.",
        "sector": "Technology",
        "keywords": ["apple", "aapl", "iphone", "macbook", "tim cook"]
    },
    "ibm": {
        "ticker": "IBM",
        "full_name": "International Business Machines",
        "sector": "Technology",
        "keywords": ["ibm", "international business machines", "watson", "mainframe"]
    },
    "microsoft": {
        "ticker": "MSFT",
        "full_name": "Microsoft Corporation",
        "sector": "Technology",
        "keywords": ["microsoft", "msft", "azure", "windows", "satya nadella", "copilot"]
    }
}

NLP_STOPWORDS = {
    "invest", "in", "about", "the", "a", "an", "tell", "me", "should", "i",
    "what", "is", "how", "company", "stock", "shares", "buy", "sell", "hold"
}