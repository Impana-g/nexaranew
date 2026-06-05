from fastapi import APIRouter, HTTPException
from services.kb_service import fetch_live_kb
from models.schemas import KBEntry
from core.config import SUPPORTED_COMPANIES
from typing import Dict

router = APIRouter()


@router.get("/kb/{company}", response_model=KBEntry)
async def get_company_kb(company: str):
    """
    Fetch live KB entry for a specific company.
    Supported: apple, ibm, microsoft
    """
    key = company.lower()
    if key not in SUPPORTED_COMPANIES:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{company}' not found. Supported: {list(SUPPORTED_COMPANIES.keys())}"
        )
    return await fetch_live_kb(key)


@router.get("/kb", response_model=Dict[str, KBEntry])
async def get_all_kb():
    """
    Fetch live KB for all supported companies simultaneously.
    """
    import asyncio
    keys = list(SUPPORTED_COMPANIES.keys())
    results = await asyncio.gather(*[fetch_live_kb(k) for k in keys])
    return dict(zip(keys, results))


@router.get("/companies")
def list_supported_companies():
    """List all supported companies with metadata."""
    return {
        key: {
            "full_name": meta["full_name"],
            "ticker": meta["ticker"],
            "sector": meta["sector"]
        }
        for key, meta in SUPPORTED_COMPANIES.items()
    }