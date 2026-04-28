import os
import pytest
from src.tools.chart_generator import generate_multimodal_chart
from src.tools.openbb_fetcher import get_momentum_indicators

def test_chart_generation():
    ticker = "AAPL"
    filepath = generate_multimodal_chart(ticker, "daily", "data/test_charts")
    assert filepath is not None
    assert os.path.exists(filepath)
    assert ticker.upper() in filepath
    # Cleanup
    if os.path.exists(filepath):
        os.remove(filepath)

def test_momentum_fetcher_live():
    # Basic live test for AAPL
    ticker = "AAPL"
    res = get_momentum_indicators(ticker)
    assert "error" not in res
    assert "rsi_14" in res
    assert "macd" in res
    assert isinstance(res["rsi_14"], (int, float))
