import pytest
import asyncio
import pandas as pd
from src.tools.openbb_fetcher import get_growth_metrics, get_momentum_indicators

@pytest.mark.asyncio
async def test_historical():
    ticker = "AAPL"
    past_date = "2023-01-01"
    
    print(f"--- Testing {ticker} as of {past_date} ---")
    
    growth = get_growth_metrics(ticker, end_date=past_date)
    print("\nHistorical Growth Metrics:")
    print(growth)
    
    momentum = get_momentum_indicators(ticker, end_date=past_date)
    print("\nHistorical Momentum Indicators:")
    print(momentum)

if __name__ == "__main__":
    asyncio.run(test_historical())
