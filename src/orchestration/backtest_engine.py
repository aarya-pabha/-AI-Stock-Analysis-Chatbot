import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import asyncio
import json
import numpy as np
import re

from src.orchestration.schemas import UserContext, FinalReport
from src.orchestration.workflow import create_trading_workflow, TradingState

logger = logging.getLogger(__name__)

class TradeSimulator:
    """Simulates the outcome of a trade based on forward price action."""
    
    @staticmethod
    def audit_trade(ticker: str, entry_date: str, entry_price: float, stop_loss: float, take_profit: float, direction: str = "Long", horizon_days: int = 21) -> Dict[str, Any]:
        """
        Checks if the Take-Profit or Stop-Loss was hit within the horizon.
        """
        # Fetch forward data (add buffer for weekends/holidays)
        start_dt = datetime.strptime(entry_date, "%Y-%m-%d")
        end_dt = start_dt + timedelta(days=horizon_days + 15)
        
        try:
            df = yf.download(ticker, start=entry_date, end=end_dt.strftime("%Y-%m-%d"), progress=False)
            if df.empty:
                return {"outcome": "No Data", "pnl_pct": 0.0, "days_held": 0, "exit_date": entry_date}
            
            # Robust MultiIndex handling
            if isinstance(df.columns, pd.MultiIndex):
                if 'High' in df.columns.get_level_values(0):
                    df.columns = df.columns.get_level_values(0)
                else:
                    df.columns = df.columns.get_level_values(1)
            
            # Use only the requested horizon window
            df = df.head(horizon_days)
            
            for i, (date, row) in enumerate(df.iterrows()):
                high = float(row['High'])
                low = float(row['Low'])
                
                if direction == "Long":
                    if low <= stop_loss:
                        pnl = ((stop_loss - entry_price) / entry_price) * 100
                        return {"outcome": "Stopped Out", "exit_price": stop_loss, "exit_date": date.strftime("%Y-%m-%d"), "pnl_pct": round(pnl, 2), "days_held": i + 1}
                    if high >= take_profit:
                        pnl = ((take_profit - entry_price) / entry_price) * 100
                        return {"outcome": "Target Hit", "exit_price": take_profit, "exit_date": date.strftime("%Y-%m-%d"), "pnl_pct": round(pnl, 2), "days_held": i + 1}
                else: # Short
                    if high >= stop_loss:
                        # Loss for a short
                        pnl = ((entry_price - stop_loss) / entry_price) * 100
                        return {"outcome": "Stopped Out", "exit_price": stop_loss, "exit_date": date.strftime("%Y-%m-%d"), "pnl_pct": round(pnl, 2), "days_held": i + 1}
                    if low <= take_profit:
                        # Profit for a short
                        pnl = ((entry_price - take_profit) / entry_price) * 100
                        return {"outcome": "Target Hit", "exit_price": take_profit, "exit_date": date.strftime("%Y-%m-%d"), "pnl_pct": round(pnl, 2), "days_held": i + 1}
            
            # If neither hit, exit at close of horizon
            final_close = float(df['Close'].iloc[-1])
            if direction == "Long":
                pnl = ((final_close - entry_price) / entry_price) * 100
            else:
                pnl = ((entry_price - final_close) / entry_price) * 100
                
            return {
                "outcome": "Timed Out",
                "exit_price": round(final_close, 2),
                "exit_date": df.index[-1].strftime("%Y-%m-%d"),
                "pnl_pct": round(pnl, 2),
                "days_held": len(df)
            }
            
        except Exception as e:
            logger.error(f"Trade simulation failed: {e}")
            return {"outcome": f"Error: {e}", "pnl_pct": 0.0, "days_held": 0, "exit_date": entry_date}

class BacktestEngine:
    """Orchestrates the walk-forward simulation with stateful position management."""
    
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
            if curr.weekday() < 5:
                dates.append(curr.strftime("%Y-%m-%d"))
            curr += timedelta(days=self.interval_days)
        return dates

    async def run(self):
        """Runs the backtest loop with position lockout."""
        sim_dates = self.get_simulation_dates()
        logger.info(f"Starting bi-directional backtest for {self.ticker} across {len(sim_dates)} dates.")
        
        import os
        os.environ["BACKTEST_MODE"] = "true"
        
        active_trade = None
        
        for date in sim_dates:
            logger.info(f"Simulating Day: {date}")
            
            # Position Check: If we have an active trade, skip analysis until it closes
            if active_trade:
                exit_dt = datetime.strptime(active_trade["exit_date"], "%Y-%m-%d")
                curr_dt = datetime.strptime(date, "%Y-%m-%d")
                
                if curr_dt <= exit_dt:
                    yield {"date": date, "status": f"HOLDING {active_trade['direction']} (Opened {active_trade['date']}). Skipping analysis."}
                    continue
                else:
                    logger.info(f"Previous trade {active_trade['direction']} closed on {active_trade['exit_date']}. Resuming analysis.")
                    active_trade = None

            # Fetch Next-Day Open for realistic entry
            tkr = yf.Ticker(self.ticker)
            start_dt = datetime.strptime(date, "%Y-%m-%d")
            fetch_end = start_dt + timedelta(days=7)
            hist = tkr.history(start=start_dt.strftime("%Y-%m-%d"), end=fetch_end.strftime("%Y-%m-%d"))
            
            next_open = None
            if len(hist) > 1:
                # hist[0] is current date, hist[1] is next trading day
                next_open = round(float(hist['Open'].iloc[1]), 2)
            elif len(hist) == 1:
                next_open = round(float(hist['Open'].iloc[0]), 2)
            
            if next_open is None:
                yield {"date": date, "status": "Failed to fetch next_open_price. Skipping."}
                continue

            yield {"date": date, "status": f"Analyzing (Next-Day Open: ${next_open})..."}
            
            context = UserContext(
                ticker=self.ticker,
                current_position="None",
                risk_tolerance="Moderate",
                investment_horizon="Short-Term",
                simulated_date=date,
                next_open_price=next_open
            )
            
            state = TradingState(context=context, simulated_date=date)
            
            try:
                workflow = create_trading_workflow()
                response = await workflow.run(state)
                final_report_raw = response.state.final_report
                
                if not final_report_raw:
                    continue

                json_match = re.search(r"(\{.*\})", final_report_raw, re.DOTALL)
                if not json_match:
                    yield {"date": date, "status": "No Trade (Invalid Format)"}
                    continue
                
                clean_json = json_match.group(1)

                try:
                    report_data = json.loads(clean_json)
                    # Support Buy (Long) and Sell (Short)
                    signal = report_data.get("short_term_signal", "Hold")
                    
                    if signal in ["Buy", "Sell"]:
                        direction = "Long" if signal == "Buy" else "Short"
                        math = report_data.get("actionable_math", {})
                        sl = math.get("stop_loss_price")
                        tp = math.get("take_profit_price")
                        
                        if sl and tp:
                            # Use next_open as the actual execution price
                            audit = TradeSimulator.audit_trade(self.ticker, date, next_open, sl, tp, direction=direction)
                            result = {
                                "date": date,
                                "signal": signal,
                                "direction": direction,
                                "entry": next_open,
                                "sl": sl,
                                "tp": tp,
                                **audit
                            }
                            self.results.append(result)
                            active_trade = result
                            yield result
                        else:
                            yield {"date": date, "status": f"{signal} signal but missing math targets."}
                    else:
                        yield {"date": date, "status": f"No Trade ({signal})"}
                except Exception as parse_err:
                    yield {"date": date, "status": "Analysis Error (Parse Failed)"}
            except Exception as e:
                yield {"date": date, "status": f"Workflow Error: {str(e)[:50]}"}
        
        # Calculate Final Metrics
        if not self.results:
            yield {"summary": "No trades executed during backtest."}
            return

        pnls = [r['pnl_pct'] for r in self.results]
        win_rate = (len([p for p in pnls if p > 0]) / len(pnls)) * 100
        total_pnl = sum(pnls)
        avg_pnl = np.mean(pnls)
        std_pnl = np.std(pnls) if len(pnls) > 1 else 0
        sharpe = (avg_pnl / std_pnl) * np.sqrt(252 / self.interval_days) if std_pnl > 0 else 0
        
        summary = {
            "ticker": self.ticker,
            "total_trades": len(self.results),
            "win_rate": round(win_rate, 2),
            "total_pnl_pct": round(total_pnl, 2),
            "avg_pnl_pct": round(float(avg_pnl), 2),
            "sharpe_ratio": round(float(sharpe), 2),
            "start_date": self.start_date,
            "end_date": self.end_date
        }
        
        logger.info(f"Backtest Summary: {summary}")
        yield {"summary": summary}
        return
