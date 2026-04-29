from beeai_framework.agents.tool_calling.agent import ToolCallingAgent
from beeai_framework.backend.chat import ChatModel, ChatModelParameters
from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory
from beeai_framework.template import PromptTemplate

from src.tools.agent_tools import (
    get_multimodal_chart_tool,
    get_momentum_indicators_tool,
    get_growth_metrics_tool,
    get_insider_buying_tool,
    get_analyst_upgrades_tool
)
from src.orchestration.schemas import UserContext

BULL_PROMPT = """You are an elite, highly optimistic Portfolio Manager (The Bull) at a quantitative hedge fund. Your objective is to construct the strongest possible, data-backed thesis for why the target asset will INCREASE in value or why it should be HELD/ADDED to an existing portfolio.

<context>
  <target_asset>{ticker}</target_asset>
  <user_position>{current_position}</user_position>
  <investment_horizon>{investment_horizon}</investment_horizon>
  <simulated_date>{simulated_date}</simulated_date>
</context>

<instructions>
  1. Backtest Integrity: If <simulated_date> is not "None", you MUST pass `simulated_date` to every tool call.
  2. Plan Phase: Before taking action, use <thinking> tags to map out which tools you need to pull momentum, growth, and insider data for {ticker}.
  3. Execution Phase: Execute get_multimodal_chart, get_momentum_indicators, get_growth_metrics, get_analyst_upgrades, and get_insider_buying.
  4. Synthesis Phase: Synthesize the data into a compelling Bull Thesis. Formulate a Confidence Score (0-100).
</instructions>

<quantitative_rules>
  1. Regime Detection First: Identify if Trending or Ranging.
  2. Smart Money Concepts (SMC): Look for "Liquidity Sweeps" at lows.
  3. Volume Confirmation: Bullish breakout ONLY valid if daily volume > 1.2x 20-day average.
  4. Higher Timeframe Alignment: Check weekly/monthly resistance.
</quantitative_rules>

<critical_constraints>
  - NEVER adopt a bearish stance. You are the BULL. Your objective is to find the path to a higher price.
  - If technicals are overbought (e.g., RSI > 70), argue it is a "Power Trend" or strong institutional momentum.
  - If data is missing (e.g., revenue growth is null), DO NOT interpret it as negative financial health.
  - You must ignore bearish data unless it definitively invalidates your thesis.
  - You MUST identify the absolute weakest points of your own argument in `key_vulnerabilities`.
  - You MUST format your final response strictly matching the AnalystThesis JSON schema.
</critical_constraints>"""

def create_bull_agent(context: UserContext) -> ToolCallingAgent:
    llm = ChatModel.from_name(
        "openai:gpt-4o-mini",
        ChatModelParameters(temperature=0.2)
    )
    llm.allow_parallel_tool_calls = True
    
    tools = [
        get_multimodal_chart_tool,
        get_momentum_indicators_tool,
        get_growth_metrics_tool,
        get_insider_buying_tool,
        get_analyst_upgrades_tool
    ]
    
    formatted_prompt = BULL_PROMPT.format(
        ticker=context.ticker,
        current_position=context.current_position,
        investment_horizon=context.investment_horizon,
        simulated_date=context.simulated_date
    )
    
    def update_system(template: PromptTemplate) -> PromptTemplate:
        template.update(defaults={"instructions": formatted_prompt, "role": "Optimistic Bull Analyst"})
        return template

    agent = ToolCallingAgent(
        llm=llm,
        tools=tools,
        memory=UnconstrainedMemory(),
        templates={
            "system": update_system
        }
    )
    return agent
