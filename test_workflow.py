import asyncio
import logging
from dotenv import load_dotenv
load_dotenv()

# Set up DEBUG logging to see the agent's internal tool calls and thoughts
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

from src.orchestration.schemas import UserContext
from src.orchestration.workflow import create_trading_workflow, TradingState

async def test():
    print("Waiting 60s for Gemini quota window to reset...")
    await asyncio.sleep(60)
    print("Testing Workflow on AAPL...")
    context = UserContext(
        ticker="AAPL", 
        current_position="None", 
        risk_tolerance="Moderate", 
        investment_horizon="Short-Term"
    )
    state = TradingState(context=context)
    workflow = create_trading_workflow()
    
    try:
        response = await workflow.run(state)
        print("\n\n=== FINAL REPORT ===")
        print(response.state.final_report)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
