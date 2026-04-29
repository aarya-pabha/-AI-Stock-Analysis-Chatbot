import asyncio
import logging
from src.orchestration.backtest_engine import BacktestEngine

# Setup logging
logging.basicConfig(level=logging.INFO)

async def run_mini_backtest():
    # Run NVDA backtest for 2 dates in early 2024
    engine = BacktestEngine(ticker="NVDA", start_date="2024-01-01", end_date="2024-01-15", interval_days=7)
    
    print("--- Starting Mini Backtest ---")
    async for result in engine.run():
        if "summary" in result:
            print("\n--- FINAL SUMMARY ---")
            print(result["summary"])
        elif "status" in result:
            print(f"Date: {result['date']} | Status: {result['status']}")
        else:
            print(f"Date: {result['date']} | Signal: {result['signal']} | PnL: {result['pnl_pct']}%")

if __name__ == "__main__":
    asyncio.run(run_mini_backtest())
