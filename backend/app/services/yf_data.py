import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict


async def fetch_historical_prices(ticker: str, days: int = 60) -> List[Dict]:
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)
    print(f"Fetching historical prices for {ticker} from {start_date} to {end_date}")

    # auto_adjust is now True by default, just being explicit
    data = yf.download(
        ticker,
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        auto_adjust=True,
    )

    if data.empty:
        return []

    # If 'Close' is multi-indexed (e.g., when ticker is a list), select the series directly
    if isinstance(data["Close"], pd.DataFrame):
        close_series = data["Close"][ticker]
    else:
        close_series = data["Close"]

    result = [
        {"date": date.strftime("%Y-%m-%d"), "close": round(close, 2)}
        for date, close in close_series.items()
    ]

    return result


async def fetch_current_price(ticker: str) -> float:
    stock = yf.Ticker(ticker)
    price = stock.info.get("regularMarketPrice")
    if not price:
        raise ValueError(f"⚠️ No real-time price available for {ticker}")
    return round(price, 2)
