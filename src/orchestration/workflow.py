import asyncio
import logging
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


async def step_drafting(state: TradingState) -> WorkflowStep:
    """Step 1: Bull and Bear independently draft their initial theses."""
    logger.info("Starting Phase: Drafting (Iteration 0)")
    
    bull_agent = create_bull_agent(state.context)
    bear_agent = create_bear_agent(state.context)
    
    prompt = f"Analyze {state.context.ticker} and generate your initial AnalystThesis based on your persona instructions."
    
    # Run analysts concurrently for speed
    bull_task = bull_agent.run(prompt=prompt)
    bear_task = bear_agent.run(prompt=prompt)
    
    bull_resp, bear_resp = await asyncio.gather(bull_task, bear_task)
    
    state.bull_draft = bull_resp.result.text
    state.bear_draft = bear_resp.result.text
    
    logger.info("Drafting complete. Moving to Critique.")
    return "critique"

async def step_critique(state: TradingState) -> WorkflowStep:
    """Step 2: CIO reviews the drafts and acts as the 'Red Team'."""
    logger.info("Starting Phase: Critique (Iteration 1)")
    
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
    
    resp = await cio_agent.run(prompt=prompt)
    state.cio_critique = resp.result.text
    
    logger.info("CIO critique generated. Moving to Revision.")
    return "revision"

async def step_revision(state: TradingState) -> WorkflowStep:
    """Step 3: Analysts revise their theses based on CIO feedback."""
    logger.info("Starting Phase: Revision (Iteration 2)")
    
    bull_agent = create_bull_agent(state.context)
    bear_agent = create_bear_agent(state.context)
    
    # Force agents to confront the critique
    bull_prompt = f"""
    Your original thesis:
    {state.bull_draft}
    
    The CIO has provided the following critical feedback:
    {state.cio_critique}
    
    Please revise your thesis accordingly. Defend your stance with data or concede points and lower your confidence score.
    Output your final AnalystThesis.
    """
    
    bear_prompt = f"""
    Your original thesis:
    {state.bear_draft}
    
    The CIO has provided the following critical feedback:
    {state.cio_critique}
    
    Please revise your thesis accordingly. Defend your stance with data or concede points and lower your confidence score.
    Output your final AnalystThesis.
    """
    
    bull_task = bull_agent.run(prompt=bull_prompt)
    bear_task = bear_agent.run(prompt=bear_prompt)
    
    bull_resp, bear_resp = await asyncio.gather(bull_task, bear_task)
    
    state.bull_revision = bull_resp.result.text
    state.bear_revision = bear_resp.result.text
    
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
    
    resp = await cio_agent.run(prompt=prompt)
    state.final_report = resp.result.text
    
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
