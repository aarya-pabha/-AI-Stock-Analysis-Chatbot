import yfinance as yf
from beeai_framework.tools.tool import Tool
from pydantic import BaseModel, Field
from typing import Dict, Any

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

class GetMultimodalChartTool(Tool):
    name = "get_multimodal_chart"
    description = "Returns the annotated .png chart showing price action, moving averages, and volume."
    input_schema = ChartInput

    def _run(self, input_data: ChartInput) -> str:
        # Note: In a true multimodal setup, we would read the bytes and attach as an image block.
        # For now, we generate the chart and return the path, assuming the agent has context
        # or the orchestration layer intercepts this to inject the image object.
        filepath = generate_multimodal_chart(input_data.ticker, input_data.timeframe)
        if filepath:
            return f"Chart generated successfully at: {filepath}. Please analyze the visual patterns."
        return "Failed to generate chart."

class GetMomentumIndicatorsTool(Tool):
    name = "get_momentum_indicators"
    description = "Returns RSI, MACD, and Stochastic oscillators to confirm trend strength."
    input_schema = TickerInput

    def _run(self, input_data: TickerInput) -> Dict[str, Any]:
        return get_momentum_indicators(input_data.ticker)

class GetVolatilityIndicatorsTool(Tool):
    name = "get_volatility_indicators"
    description = "Returns Bollinger Bands and Average True Range (ATR) to spot overextended prices."
    input_schema = TickerInput

    def _run(self, input_data: TickerInput) -> Dict[str, Any]:
        return get_volatility_indicators(input_data.ticker)

class GetGrowthMetricsTool(Tool):
    name = "get_growth_metrics"
    description = "Returns fundamental data like YoY Revenue and EPS growth."
    input_schema = TickerInput

    def _run(self, input_data: TickerInput) -> Dict[str, Any]:
        return get_growth_metrics(input_data.ticker)

class GetRiskMetricsTool(Tool):
    name = "get_risk_metrics"
    description = "Returns fundamental risk data like Debt-to-Equity ratios and declining profit margins."
    input_schema = TickerInput

    def _run(self, input_data: TickerInput) -> Dict[str, Any]:
        return get_risk_metrics(input_data.ticker)

class GetInsiderBuyingTool(Tool):
    name = "get_insider_buying"
    description = "Returns recent open-market purchases by executives to gauge C-suite conviction."
    input_schema = TickerInput

    def _run(self, input_data: TickerInput) -> Dict[str, Any]:
        return get_insider_activity(input_data.ticker)

class GetInsiderSellingTool(Tool):
    name = "get_insider_selling"
    description = "Returns recent share dumping by executives."
    input_schema = TickerInput

    def _run(self, input_data: TickerInput) -> Dict[str, Any]:
        return get_insider_activity(input_data.ticker)

class GetAnalystUpgradesTool(Tool):
    name = "get_analyst_upgrades"
    description = "Returns recent Wall Street price target increases."
    input_schema = TickerInput

    def _run(self, input_data: TickerInput) -> Dict[str, Any]:
        return get_analyst_upgrades(input_data.ticker)

class GetShortInterestDataTool(Tool):
    name = "get_short_interest_data"
    description = "Returns percentage of float shorted and days-to-cover."
    input_schema = TickerInput

    def _run(self, input_data: TickerInput) -> Dict[str, Any]:
        return get_short_interest_data(input_data.ticker)

class CheckMarketRegimeTool(Tool):
    name = "check_market_regime"
    description = "Evaluates the S&P 500's 200-day Moving Average to determine the macro trend."
    input_schema = BaseModel  # No input needed, checks SPY directly

    def _run(self, input_data: BaseModel) -> Dict[str, Any]:
        try:
            spy = yf.Ticker("SPY")
            hist = spy.history(period="1y")
            current_price = hist['Close'].iloc[-1]
            sma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
            regime = "Bull Market" if current_price > sma_200 else "Bear Market"
            return {"spy_current": round(current_price, 2), "spy_sma_200": round(sma_200, 2), "regime": regime}
        except Exception as e:
            return {"error": str(e)}

class CheckLiquidityGateTool(Tool):
    name = "check_liquidity_gate"
    description = "Verifies if the target asset trades >1,000,000 shares a day."
    input_schema = TickerInput

    def _run(self, input_data: TickerInput) -> Dict[str, Any]:
        try:
            tkr = yf.Ticker(input_data.ticker)
            adv = tkr.info.get("averageVolume", 0)
            passed = adv >= 1000000
            return {"average_daily_volume": adv, "liquidity_gate_passed": passed}
        except Exception as e:
            return {"error": str(e)}

class RiskRewardInput(BaseModel):
    entry_price: float = Field(description="The assumed entry price.")
    atr_value: float = Field(description="The ATR value.")
    risk_tolerance: str = Field(default="Moderate", description="User's risk tolerance.")

class CalculateRiskRewardTool(Tool):
    name = "calculate_risk_reward"
    description = "Deterministic math engine that calculates exact Stop-Loss and Take-Profit targets."
    input_schema = RiskRewardInput

    def _run(self, input_data: RiskRewardInput) -> Dict[str, Any]:
        return calculate_risk_reward(input_data.entry_price, input_data.atr_value, input_data.risk_tolerance)
