import asyncio
import logging
import json
from typing import Literal, TypeAlias
from pydantic import BaseModel, Field

from beeai_framework.workflows import Workflow, WorkflowReservedStepName
from src.orchestration.schemas import UserContext
from src.agents.bull_agent import create_bull_agent
from src.agents.bear_agent import create_bear_agent
from src.agents.cio_agent import create_cio_agent

logger = logging.getLogger(__name__)

# Define the explicit steps in our Agentic Reflection Loop
WorkflowStep: TypeAlias = Literal["drafting", "critique", "revision", "judgment"]

class TradingState(BaseModel):
    """The global state object passed between agents during the workflow."""
    context: UserContext
    simulated_date: str | None = Field(default=None, description="The point-in-time cutoff (YYYY-MM-DD) for backtesting.")
    
    # Iteration 0
    bull_draft: str | None = Field(default=None, description="Draft 1 from the Bull")
    bear_draft: str | None = Field(default=None, description="Draft 1 from the Bear")
    
    # Iteration 1
    cio_critique: str | None = Field(default=None, description="CIO's critique of the drafts")
    
    # Iteration 2
    bull_revision: str | None = Field(default=None, description="Revised Bull Thesis")
    bear_revision: str | None = Field(default=None, description="Revised Bear Thesis")
    
    # Final Output
    final_report: str | None = Field(default=None, description="The final synthesized report from the CIO")


from src.tools.openbb_fetcher import (
    get_momentum_indicators,
    get_volatility_indicators,
    get_growth_metrics,
    get_risk_metrics,
    get_insider_activity,
    get_short_interest_data,
    get_analyst_upgrades
)

async def step_drafting(state: TradingState) -> WorkflowStep:
    """Step 1: Bull and Bear independently draft their initial theses with pre-fetched data."""
    logger.info(f"--- Phase: Drafting (Iteration 0) for {state.context.ticker} ---")
    
    ticker = state.context.ticker
    end_date = state.simulated_date
    
    # Pre-fetch all data with simulated end_date if provided
    logger.info(f"Pre-fetching data for {ticker} (End Date: {end_date})...")
    data_packet = {
        "momentum": get_momentum_indicators(ticker, end_date=end_date),
        "volatility": get_volatility_indicators(ticker, end_date=end_date),
        "growth": get_growth_metrics(ticker), # Fundamentals are generally point-in-time from yfinance
        "risk": get_risk_metrics(ticker),
        "insider": get_insider_activity(ticker),
        "short_interest": get_short_interest_data(ticker),
        "analyst_recs": get_analyst_upgrades(ticker)
    }
    
    bull_agent = create_bull_agent(state.context)
    bear_agent = create_bear_agent(state.context)
    
    # Update chart with end_date
    from src.tools.chart_generator import generate_multimodal_chart
    generate_multimodal_chart(ticker, timeframe="daily", end_date=end_date)
    
    data_str = json.dumps(data_packet, indent=2)
    prompt = f"""
    Analyze the following pre-fetched data and chart for {ticker}. 
    Current Simulated Date: {end_date if end_date else "Present Day"}
    Generate your initial AnalystThesis based on your persona instructions.
    
    [MARKET DATA]
    {data_str}
    
    Note: A candlestick chart image has been generated in data/{ticker}_daily_chart.png.
    """
    
    logger.info("Triggering Bull and Bear analysts in parallel...")
    # Parallel execution using asyncio.gather
    bull_task = bull_agent.run(prompt, max_iterations=10)
    bear_task = bear_agent.run(prompt, max_iterations=10)
    
    bull_resp, bear_resp = await asyncio.gather(bull_task, bear_task)
    
    state.bull_draft = bull_resp.last_message.text
    state.bear_draft = bear_resp.last_message.text
    
    logger.info("Drafting complete. Moving to Critique.")
    return "critique"

async def step_critique(state: TradingState) -> WorkflowStep:
    """Step 2: CIO reviews the drafts and acts as the 'Red Team'."""
    logger.info("--- Phase: Critique (Iteration 1) ---")
    
    cio_agent = create_cio_agent(state.context)
    
    prompt = f"""
    Review the following initial drafts from your analysts.
    
    [BULL DRAFT]
    {state.bull_draft}
    
    [BEAR DRAFT]
    {state.bear_draft}
    
    Act as the Red Team. Attack their key vulnerabilities, flag unconfirmed volume, 
    and provide explicit feedback for their required revisions. Do NOT output the Final Report yet.
    """
    
    logger.info("Triggering CIO for critique...")
    resp = await cio_agent.run(prompt, max_iterations=15)
    state.cio_critique = resp.last_message.text
    
    logger.info("CIO critique generated. Moving to Revision.")
    return "revision"

async def step_revision(state: TradingState) -> WorkflowStep:
    """Step 3: Analysts revise their theses based on CIO feedback."""
    logger.info("Starting Phase: Revision (Iteration 2)")
    
    bull_agent = create_bull_agent(state.context)
    bear_agent = create_bear_agent(state.context)
    
    bull_prompt = f"Your original thesis:\n{state.bull_draft}\n\nCIO Feedback:\n{state.cio_critique}\n\nPlease revise your AnalystThesis."
    bear_prompt = f"Your original thesis:\n{state.bear_draft}\n\nCIO Feedback:\n{state.cio_critique}\n\nPlease revise your AnalystThesis."
    
    logger.info("Triggering Analyst revisions in parallel...")
    bull_task = bull_agent.run(bull_prompt, max_iterations=10)
    bear_task = bear_agent.run(bear_prompt, max_iterations=10)
    
    bull_resp, bear_resp = await asyncio.gather(bull_task, bear_task)
    
    state.bull_revision = bull_resp.last_message.text
    state.bear_revision = bear_resp.last_message.text
    
    logger.info("Revisions complete. Moving to Final Judgment.")
    return "judgment"

async def step_judgment(state: TradingState) -> WorkflowReservedStepName:
    """Step 4: CIO enforces rules, calculates exact targets, and outputs Final Report."""
    logger.info("Starting Phase: Final Judgment")
    
    cio_agent = create_cio_agent(state.context)
    
    prompt = f"""
    Here are the revised theses from your analysts:
    
    [REVISED BULL THESIS]
    {state.bull_revision}
    
    [REVISED BEAR THESIS]
    {state.bear_revision}
    
    You must now execute your quantitative guardrails:
    1. Check Market Regime (SPY 200 SMA).
    2. Check Liquidity Gate.
    3. Run Calculate Risk/Reward math.
    
    Output the final, structured FinalReport.
    """
    
    resp = await cio_agent.run(prompt, max_iterations=15)
    state.final_report = resp.last_message.text
    
    logger.info("Workflow Complete.")
    return Workflow.END

def create_trading_workflow() -> Workflow:
    """Instantiates the stateful routing graph for the Multi-Agent Council."""
    workflow = Workflow[TradingState, WorkflowStep](name="TradingCouncilWorkflow", schema=TradingState)
    
    # Register the steps
    workflow.add_step("drafting", step_drafting)
    workflow.add_step("critique", step_critique)
    workflow.add_step("revision", step_revision)
    workflow.add_step("judgment", step_judgment)
    
    return workflow
