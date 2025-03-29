import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict


async def fetch_historical_prices(ticker: str, days: int = 60) -> List[Dict]:
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)
    print(f"Fetching historical prices for {ticker} from {start_date} to {end_date}")
    data = yf.download(
        ticker, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d")
    )

    if data.empty:
        return []

    result = []
    for index, row in data.iterrows():
        result.append(
            {"date": index.strftime("%Y-%m-%d"), "close": round(row["Close"], 2)}
        )

    return result
