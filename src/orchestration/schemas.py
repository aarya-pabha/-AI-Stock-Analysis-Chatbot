from pydantic import BaseModel, Field
from typing import Literal

class UserContext(BaseModel):
    ticker: str = Field(..., description="The exact US stock or ETF symbol (e.g., AAPL)")
    current_position: Literal["None", "Long", "Short"] = Field(
        default="None", 
        description="The user's current position in the asset."
    )
    risk_tolerance: Literal["Conservative", "Moderate", "Aggressive"] = Field(
        default="Moderate", 
        description="The user's risk tolerance, affecting position sizing and R:R."
    )
    investment_horizon: Literal["Short-Term", "Long-Term", "Both"] = Field(
        default="Both", 
        description="The horizon for the trading analysis."
    )

class AnalystThesis(BaseModel):
    agent_role: Literal["Bull", "Bear"]
    technical_argument: str = Field(description="Argument based on chart, momentum, and volatility, following 2026 regime rules.")
    fundamental_argument: str = Field(description="Argument based on growth, risk, and insider data.")
    confidence_score: int = Field(ge=0, le=100, description="Confidence in this thesis (0-100).")
    key_vulnerabilities: list[str] = Field(description="Admit the absolute weakest points of your own thesis so the CIO can evaluate.")

class FinalReport(BaseModel):
    ticker: str
    assumptions_used: UserContext
    short_term_signal: Literal["Buy", "Sell", "Hold", "Take Profit", "Cut Losses"]
    long_term_signal: Literal["Buy", "Sell", "Hold", "Take Profit", "Cut Losses"]
    cio_synthesis: str = Field(description="How the debate was resolved and risk was assessed based on the 4-Quadrant Volatility check.")
    actionable_math: dict = Field(description="Deterministic Entry, Stop-Loss, and Target derived from the Math Lab tool.")
