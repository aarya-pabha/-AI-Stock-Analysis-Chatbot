import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import asyncio
import json

from src.orchestration.schemas import UserContext, FinalReport
from src.orchestration.workflow import create_trading_workflow, TradingState

logger = logging.getLogger(__name__)

class TradeSimulator:
    """Simulates the outcome of a trade based on forward price action."""
    
    @staticmethod
    def audit_trade(ticker: str, entry_date: str, entry_price: float, stop_loss: float, take_profit: float, horizon_days: int = 21) -> Dict[str, Any]:
        """
        Checks if the Take-Profit or Stop-Loss was hit within the horizon.
        """
        # Fetch forward data (add buffer for weekends/holidays)
        start_dt = datetime.strptime(entry_date, "%Y-%m-%d")
        end_dt = start_dt + timedelta(days=horizon_days + 10)
        
        try:
            df = yf.download(ticker, start=entry_date, end=end_dt.strftime("%Y-%m-%d"), progress=False)
            if df.empty:
                return {"outcome": "No Data", "pnl_pct": 0.0, "days_held": 0}
            
            # Use only the requested horizon window
            df = df.head(horizon_days)
            
            for i, (date, row) in enumerate(df.iterrows()):
                high = row['High']
                low = row['Low']
                close = row['Close']
                
                # Logic: Check if stopped out first (conservative)
                if low <= stop_loss:
                    pnl = ((stop_loss - entry_price) / entry_price) * 100
                    return {
                        "outcome": "Stopped Out",
                        "exit_price": stop_loss,
                        "exit_date": date.strftime("%Y-%m-%d"),
                        "pnl_pct": round(pnl, 2),
                        "days_held": i + 1
                    }
                
                # Check if target hit
                if high >= take_profit:
                    pnl = ((take_profit - entry_price) / entry_price) * 100
                    return {
                        "outcome": "Target Hit",
                        "exit_price": take_profit,
                        "exit_date": date.strftime("%Y-%m-%d"),
                        "pnl_pct": round(pnl, 2),
                        "days_held": i + 1
                    }
            
            # If neither hit, exit at close of horizon
            final_close = df['Close'].iloc[-1]
            pnl = ((final_close - entry_price) / entry_price) * 100
            return {
                "outcome": "Timed Out (Closed at Horizon)",
                "exit_price": round(final_close, 2),
                "exit_date": df.index[-1].strftime("%Y-%m-%d"),
                "pnl_pct": round(pnl, 2),
                "days_held": len(df)
            }
            
        except Exception as e:
            logger.error(f"Trade simulation failed: {e}")
            return {"outcome": f"Error: {e}", "pnl_pct": 0.0, "days_held": 0}

class BacktestEngine:
    """Orchestrates the walk-forward simulation across historical dates."""
    
    def __init__(self, ticker: str, start_date: str, end_date: str, interval_days: int = 7):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.interval_days = interval_days
        self.results: List[Dict[str, Any]] = []

    def get_simulation_dates(self) -> List[str]:
        """Generates a list of dates to run the agent on."""
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.strptime(self.end_date, "%Y-%m-%d")
        
        dates = []
        curr = start
        while curr <= end:
            # Simple check: skip weekends for simulation efficiency
            if curr.weekday() < 5:
                dates.append(curr.strftime("%Y-%m-%d"))
            curr += timedelta(days=self.interval_days)
        return dates

    async def run(self) -> List[Dict[str, Any]]:
        """Runs the backtest loop."""
        sim_dates = self.get_simulation_dates()
        logger.info(f"Starting backtest for {self.ticker} across {len(sim_dates)} dates.")
        
        # Ensure BACKTEST_MODE is true for cost optimization
        import os
        os.environ["BACKTEST_MODE"] = "true"
        
        for date in sim_dates:
            logger.info(f"Simulating Day: {date}")
            
            context = UserContext(
                ticker=self.ticker,
                current_position="None",
                risk_tolerance="Moderate",
                investment_horizon="Short-Term"
            )
            
            # Initialize state with the simulated end_date
            state = TradingState(context=context, simulated_date=date)
            
            try:
                workflow = create_trading_workflow()
                response = await workflow.run(state)
                final_state = response.state
                
                # Check for "Buy" signal with confidence > 75%
                # We need to parse the JSON string from final_report
                try:
                    report_data = json.loads(final_state.final_report)
                    signal = report_data.get("short_term_signal", "Hold")
                    # We'll assume the CIO synthesizes a confidence score or we extract it
                    # For now, if it's a Buy, we simulate it
                    
                    if signal == "Buy":
                        math = report_data.get("actionable_math", {})
                        entry = math.get("entry_price")
                        sl = math.get("stop_loss_price")
                        tp = math.get("take_profit_price")
                        
                        if entry and sl and tp:
                            audit = TradeSimulator.audit_trade(self.ticker, date, entry, sl, tp)
                            result = {
                                "date": date,
                                "signal": signal,
                                "entry": entry,
                                "sl": sl,
                                "tp": tp,
                                **audit
                            }
                            self.results.append(result)
                            logger.info(f"Trade Result for {date}: {audit['outcome']} ({audit['pnl_pct']}%)")
                except Exception as parse_err:
                    logger.error(f"Failed to parse FinalReport for {date}: {parse_err}")
                    
            except Exception as e:
                logger.error(f"Workflow failed for {date}: {e}")
            
        return self.results
