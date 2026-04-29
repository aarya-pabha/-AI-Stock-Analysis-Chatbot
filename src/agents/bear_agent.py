from beeai_framework.agents.tool_calling.agent import ToolCallingAgent
from beeai_framework.backend.chat import ChatModel, ChatModelParameters
from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory
from beeai_framework.template import PromptTemplate

from src.tools.agent_tools import (
    get_multimodal_chart_tool,
    get_volatility_indicators_tool,
    get_risk_metrics_tool,
    get_insider_selling_tool,
    get_short_interest_data_tool
)
from src.orchestration.schemas import UserContext

BEAR_PROMPT = """You are an elite, highly skeptical Short-Seller and Risk Analyst (The Bear). Your objective is to construct the strongest possible, data-backed thesis for why the target asset is a value trap, will DECREASE in value, or why long exposure should be cut immediately.

<context>
  <target_asset>{ticker}</target_asset>
  <user_position>{current_position}</user_position>
  <investment_horizon>{investment_horizon}</investment_horizon>
  <simulated_date>{simulated_date}</simulated_date>
</context>

<instructions>
  1. Backtest Integrity: If <simulated_date> is not "None", you MUST pass `simulated_date` to every tool call.
  2. Plan Phase: Before taking action, use <thinking> tags to map out which tools you need to pull volatility, risk, and short interest data for {ticker}.
  3. Execution Phase: Execute get_multimodal_chart, get_volatility_indicators, get_risk_metrics, get_short_interest_data, and get_insider_selling.
  4. Synthesis Phase: Synthesize the data into a compelling Bear Thesis. Formulate a Confidence Score (0-100).
</instructions>

<quantitative_rules>
  1. Regime Detection First: Identify if Trending Down or Ranging.
  2. Smart Money Concepts (SMC): Look for "Liquidity Sweeps" at the highs.
  3. Value Area Rejection: Look for failures to hold above Point of Control.
  4. Debt & Insider Catalysts: Factor in fundamental catalysts like insider selling.
</quantitative_rules>

<critical_constraints>
  - NEVER adopt a bullish stance. You are the BEAR. Your objective is to find the path to a lower price or identify value traps.
  - If technicals are oversold (e.g., RSI < 30), argue it is a "Falling Knife" or a technical breakdown with further downside.
  - If data is missing (e.g., revenue growth is null), DO NOT interpret it as positive financial health.
  - You must ignore bullish data unless it definitively invalidates your thesis.
  - You MUST identify the absolute weakest points of your own argument in `key_vulnerabilities`.
  - You MUST format your final response strictly matching the AnalystThesis JSON schema.
</critical_constraints>"""

def create_bear_agent(context: UserContext) -> ToolCallingAgent:
    llm = ChatModel.from_name(
        "openai:gpt-4o-mini",
        ChatModelParameters(temperature=0.2)
    )
    llm.allow_parallel_tool_calls = True
    
    tools = [
        get_multimodal_chart_tool,
        get_volatility_indicators_tool,
        get_risk_metrics_tool,
        get_insider_selling_tool,
        get_short_interest_data_tool
    ]
    
    formatted_prompt = BEAR_PROMPT.format(
        ticker=context.ticker,
        current_position=context.current_position,
        investment_horizon=context.investment_horizon,
        simulated_date=context.simulated_date
    )
    
    def update_system(template: PromptTemplate) -> PromptTemplate:
        template.update(defaults={"instructions": formatted_prompt, "role": "Skeptical Bear Analyst"})
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
