import os
import uuid
from typing import Optional
import httpx
import logging

logger = logging.getLogger("stocksense")

FMP_API_KEY = os.getenv("FMP_API_KEY")
FMP_PROFILE_URL = os.getenv("FMP_PROFILE_URL")
UUID_NAMESPACE = os.getenv("UUID_NAMESPACE")
if not UUID_NAMESPACE:
    raise RuntimeError("UUID_NAMESPACE is not set")
NAMESPACE = uuid.UUID(UUID_NAMESPACE)


def generate_stable_uuid(ticker: str, exchange: str) -> str:
    key = f"{ticker.upper()}_{exchange.upper()}"
    return str(uuid.uuid5(NAMESPACE, key))


async def fetch_company_profile_async(ticker: str) -> Optional[dict]:
    url = f"{FMP_PROFILE_URL}/{ticker}?apikey={FMP_API_KEY}"

    async with httpx.AsyncClient(timeout=5) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"❌ Error fetching FMP profile for {ticker}: {e}")
            return None

    if not data or not isinstance(data, list) or len(data) == 0:
        logger.warning(f"⚠️ No profile found in FMP for {ticker}")
        return None

    p = data[0]
    exchange = p.get("exchangeShortName") or "UNKNOWN"
    generated_id = generate_stable_uuid(p["symbol"], exchange)

    return {
        "id": generated_id,
        "ticker": p.get("symbol"),
        "name": p.get("companyName"),
        "shortname": None,
        "exchange": exchange,
        "sector": p.get("sector"),
        "industry": p.get("industry"),
        "country": p.get("country") or "USA",
        "website": p.get("website"),
        "summary": p.get("description"),
        "ceo": p.get("ceo"),
        "ipo_date": p.get("ipoDate"),
        "image": p.get("image"),
        "phone": p.get("phone"),
        "address": p.get("address"),
        "city": p.get("city"),
        "state": p.get("state"),
        "zip": p.get("zip"),
        # Financials
        "current_price": p.get("price"),
        "market_cap": p.get("mktCap"),
        "ebitda": None,  # not in this API response
        "revenue_growth": None,  # not in this API response
        "vol_avg": p.get("volAvg"),
        "beta": p.get("beta"),
        "last_dividend": p.get("lastDiv"),
        "range_52w": p.get("range"),
        "dcf": p.get("dcf"),
        "dcf_diff": p.get("dcfDiff"),
        "currency": p.get("currency"),
        # Flags
        "is_etf": p.get("isEtf"),
        "is_adr": p.get("isAdr"),
        "is_fund": p.get("isFund"),
        "is_actively_trading": p.get("isActivelyTrading"),
        # Employees
        "fulltime_employees": (
            int(p["fullTimeEmployees"])
            if p.get("fullTimeEmployees") and str(p["fullTimeEmployees"]).isdigit()
            else None
        ),
        "created_at": None,
    }
