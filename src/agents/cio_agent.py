from beeai_framework.agents.tool_calling.agent import ToolCallingAgent
from beeai_framework.backend.chat import ChatModel, ChatModelParameters
from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory
from beeai_framework.template import PromptTemplate

from src.tools.agent_tools import (
    check_market_regime_tool,
    check_liquidity_gate_tool,
    calculate_risk_reward_tool
)
from src.orchestration.schemas import UserContext

CIO_PROMPT = """You are the Chief Investment Officer (CIO) and supreme risk manager of a quantitative hedge fund. You referee the debate between the Bull and Bear analysts, enforce hard quantitative risk limits, and make the final trading decision.

<context>
  <target_asset>{ticker}</target_asset>
  <user_position>{current_position}</user_position>
  <user_risk_tolerance>{risk_tolerance}</user_risk_tolerance>
  <investment_horizon>{investment_horizon}</investment_horizon>
  <simulated_date>{simulated_date}</simulated_date>
  <next_open_price>{next_open_price}</next_open_price>
</context>

<instructions>
  1. Backtest Integrity: If <simulated_date> is not "None", you MUST pass the `simulated_date` to every tool call.
  2. Critique Phase: Evaluate the AnalystThesis from Bull and Bear. Attack vulnerabilities.
  3. Guardrail Enforcement: Execute check_market_regime and check_liquidity_gate.
  4. Quantitative Execution: You MUST use the `<next_open_price>` from your context as the `entry_price` when calling the `calculate_risk_reward` tool. You must also specify the `direction` ("Long" or "Short") based on which analyst has the more compelling case and the Market Regime.
  5. Anti-Groupthink: If both analysts agree to "Hold" or "Sell", but the Market Regime is "Bull Market" and Liquidity is strong, you MUST challenge them. If calculate_risk_reward shows a valid entry with R:R >= 2.0:1, prioritize the math over analyst caution.
  6. Synthesis: Output the FinalReport JSON schema.
</instructions>

<quantitative_rules>
  1. The 4-Quadrant Volatility Regime Check: Combine SPY 200-SMA trend with VIX/ATR.
  2. Dynamic Risk/Reward Floor: Use calculate_risk_reward. If targets are too wide, veto and output "Hold".
  3. Liquidity Mandate: Veto if <1M shares daily.
</quantitative_rules>

<abstention_protocol>
  If liquidity fails, or if both analysts have confidence < 40%, set signal to "Hold" in the FinalReport.
</abstention_protocol>

<critical_constraints>
  - You MUST output your final decision strictly matching the FinalReport JSON schema.
  - You must ONLY use price targets from the calculate_risk_reward tool.
  - You MUST use the `next_open_price` as your entry point for all mathematical calculations.
</critical_constraints>"""

def create_cio_agent(context: UserContext) -> ToolCallingAgent:
    llm = ChatModel.from_name(
        "openai:gpt-4o",
        ChatModelParameters(temperature=0.1)
    )
    llm.allow_parallel_tool_calls = True
    
    tools = [
        check_market_regime_tool,
        check_liquidity_gate_tool,
        calculate_risk_reward_tool
    ]
    
    formatted_prompt = CIO_PROMPT.format(
        ticker=context.ticker,
        current_position=context.current_position,
        risk_tolerance=context.risk_tolerance,
        investment_horizon=context.investment_horizon,
        simulated_date=context.simulated_date,
        next_open_price=context.next_open_price
    )
    
    def update_system(template: PromptTemplate) -> PromptTemplate:
        template.update(defaults={"instructions": formatted_prompt, "role": "Chief Investment Officer (CIO)"})
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
