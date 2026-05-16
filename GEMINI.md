# Project Context: AI Stock Analysis Chatbot (V1.0 Finished)

## 🎯 Current Status
**Phase:** Stage 5 (Institutional Integration) COMPLETE.
**Goal:** Institutional-grade multi-agent stock analysis with bi-directional walk-forward backtesting (FINSABER Standard).

## 🛠️ Tech Stack & Configuration (Source of Truth)
- **Orchestration:** BeeAI Framework (Stateful Workflow).
- **Models:** CIO Judge (`gpt-4o`), Analysts (`gpt-4o-mini`).
- **Data:** OpenBB v4 (Technical/Fundamentals) + yfinance (Price).
- **UI:** Gradio `v5.50.0` (Pinned for stability).

## 🧠 Core Architectural Constraints (DO NOT REVERT)

### 1. Multi-Agent Council Structure
- **Agent A (Bull)**: Optimized for upside thesis using `get_momentum_indicators`, `get_growth_metrics`, `get_insider_buying`, and `get_analyst_upgrades`.
- **Agent B (Bear)**: Optimized for risk/downside using `get_volatility_indicators`, `get_risk_metrics`, `get_insider_selling`, and `get_short_interest_data`.
- **Agent C (CIO)**: Final referee enforcing quantitative gates via `check_market_regime`, `check_liquidity_gate`, and `calculate_risk_reward`.

### 2. State & Workflow Gating
- **Pydantic Validation**: All agent handoffs must use `AnalystThesis` or `FinalReport` schemas (found in `src/orchestration/schemas.py`).
- **Workflow Steps**: The BeeAI workflow must strictly follow the names: `drafting`, `critique`, `revision`, and `judgment`.
- **Reflection Loop**: The CIO MUST act as a "Red Team" in the `critique` step, challenging analysts to revise their thesis in the `revision` step.

### 3. Quantitative Execution
- **Realistic Slippage**: Trades in `BacktestEngine` and `calculate_risk_reward` MUST use the **Next-Day Market Open** as the entry point.
- **Bi-Directional Signal**: Support both "Long" and "Short" positions with inverted Stop-Loss/Take-Profit ATR math.
- **Anti-Groupthink**: CIO is hard-coded to prioritize quantitative math (R:R) over analyst caution if the Market Regime is bullish and Liquidity is strong.

## 🚀 Operations
1. **Resume Development**: Activate venv (`.\venv\Scripts\activate`) and run `python main.py`.
2. **Backtesting**: Use `tests/run_mini_backtest.py` for walk-forward verification.
3. **Deployment**: Pre-configured for Hugging Face Spaces via `Dockerfile` and `requirements.txt`.

---
*Reference current implementation in `src/orchestration/workflow.py` before modifying core logic.*
