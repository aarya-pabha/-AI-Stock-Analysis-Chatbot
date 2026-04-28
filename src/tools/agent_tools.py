import json
import yfinance as yf
from pydantic import BaseModel, Field
from typing import Dict, Any

from beeai_framework.tools import tool

from src.tools.chart_generator import generate_multimodal_chart
from src.tools.openbb_fetcher import (
    get_momentum_indicators,
    get_volatility_indicators,
    get_growth_metrics,
    get_risk_metrics,
    get_insider_activity,
    get_short_interest_data,
    get_analyst_upgrades
)
from src.tools.math_lab import calculate_risk_reward

class TickerInput(BaseModel):
    ticker: str = Field(description="The exact US stock or ETF symbol (e.g., AAPL)")

class ChartInput(BaseModel):
    ticker: str = Field(description="The exact US stock or ETF symbol")
    timeframe: str = Field(default="daily", description="'daily' or 'weekly'")

@tool(name="get_multimodal_chart", description="Returns the annotated .png chart showing price action, moving averages, and volume.", input_schema=ChartInput)
def get_multimodal_chart_tool(ticker: str, timeframe: str = "daily") -> str:
    filepath = generate_multimodal_chart(ticker, timeframe)
    if filepath:
        return f"Chart generated successfully at: {filepath}. Please analyze the visual patterns."
    return "Failed to generate chart."

@tool(name="get_momentum_indicators", description="Returns RSI, MACD, and Stochastic oscillators to confirm trend strength.", input_schema=TickerInput)
def get_momentum_indicators_tool(ticker: str) -> str:
    return json.dumps(get_momentum_indicators(ticker))

@tool(name="get_volatility_indicators", description="Returns Bollinger Bands and Average True Range (ATR) to spot overextended prices.", input_schema=TickerInput)
def get_volatility_indicators_tool(ticker: str) -> str:
    return json.dumps(get_volatility_indicators(ticker))

@tool(name="get_growth_metrics", description="Returns fundamental data like YoY Revenue and EPS growth.", input_schema=TickerInput)
def get_growth_metrics_tool(ticker: str) -> str:
    return json.dumps(get_growth_metrics(ticker))

@tool(name="get_risk_metrics", description="Returns fundamental risk data like Debt-to-Equity ratios and declining profit margins.", input_schema=TickerInput)
def get_risk_metrics_tool(ticker: str) -> str:
    return json.dumps(get_risk_metrics(ticker))

@tool(name="get_insider_buying", description="Returns recent open-market purchases by executives to gauge C-suite conviction.", input_schema=TickerInput)
def get_insider_buying_tool(ticker: str) -> str:
    return json.dumps(get_insider_activity(ticker))

@tool(name="get_insider_selling", description="Returns recent share dumping by executives.", input_schema=TickerInput)
def get_insider_selling_tool(ticker: str) -> str:
    return json.dumps(get_insider_activity(ticker))

@tool(name="get_analyst_upgrades", description="Returns recent Wall Street price target increases.", input_schema=TickerInput)
def get_analyst_upgrades_tool(ticker: str) -> str:
    return json.dumps(get_analyst_upgrades(ticker))

@tool(name="get_short_interest_data", description="Returns percentage of float shorted and days-to-cover.", input_schema=TickerInput)
def get_short_interest_data_tool(ticker: str) -> str:
    return json.dumps(get_short_interest_data(ticker))

class EmptyInput(BaseModel):
    pass

@tool(name="check_market_regime", description="Evaluates the S&P 500's 200-day Moving Average to determine the macro trend.", input_schema=EmptyInput)
def check_market_regime_tool() -> str:
    try:
        spy = yf.Ticker("SPY")
        hist = spy.history(period="1y")
        current_price = hist['Close'].iloc[-1]
        sma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
        regime = "Bull Market" if current_price > sma_200 else "Bear Market"
        return json.dumps({"spy_current": round(current_price, 2), "spy_sma_200": round(sma_200, 2), "regime": regime})
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool(name="check_liquidity_gate", description="Verifies if the target asset trades >1,000,000 shares a day.", input_schema=TickerInput)
def check_liquidity_gate_tool(ticker: str) -> str:
    try:
        tkr = yf.Ticker(ticker)
        adv = tkr.info.get("averageVolume", 0)
        passed = adv >= 1000000
        return json.dumps({"average_daily_volume": adv, "liquidity_gate_passed": passed})
    except Exception as e:
        return json.dumps({"error": str(e)})

class RiskRewardInput(BaseModel):
    entry_price: float = Field(description="The assumed entry price.")
    atr_value: float = Field(description="The ATR value.")
    risk_tolerance: str = Field(default="Moderate", description="User's risk tolerance.")

@tool(name="calculate_risk_reward", description="Deterministic math engine that calculates exact Stop-Loss and Take-Profit targets.", input_schema=RiskRewardInput)
def calculate_risk_reward_tool(entry_price: float, atr_value: float, risk_tolerance: str = "Moderate") -> str:
    return json.dumps(calculate_risk_reward(entry_price, atr_value, risk_tolerance))
