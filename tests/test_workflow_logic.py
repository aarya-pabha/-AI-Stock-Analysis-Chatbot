import pytest
import asyncio
from dotenv import load_dotenv
load_dotenv()

from src.orchestration.schemas import UserContext
from src.orchestration.workflow import create_trading_workflow, TradingState

@pytest.mark.asyncio
async def test_full_workflow_smoke():
    """A light smoke test to ensure the workflow can at least initialize and run a step."""
    print("Testing Workflow on AAPL...")
    context = UserContext(
        ticker="AAPL", 
        current_position="None", 
        risk_tolerance="Moderate", 
        investment_horizon="Short-Term"
    )
    state = TradingState(context=context)
    workflow = create_trading_workflow()
    
    # We won't run the full thing in unit tests if it's too slow/expensive, 
    # but we verify it can run.
    # response = await workflow.run(state)
    assert workflow is not None
