# Project Context: AI Stock Analysis Chatbot

## 🎯 Current Status
**Phase:** Stage 2 (Institutional Backtesting) Complete & Verified.
**Goal:** Institutional-grade multi-agent stock analysis with point-in-time backtesting.

## 🛠️ Tech Stack & Configuration
- **Orchestration:** BeeAI Framework (Stateful Workflow).
- **LLM Models:** 
  - CIO Judge: `openai:gpt-4o`
  - Analysts: `openai:gpt-4o-mini`
- **Data:** OpenBB v4 (Technical + Fundamentals) + yfinance (OHLCV).
- **Vision:** `mplfinance` generating `.png` charts for VLM analysis.

## 🧠 Core Architectural Decisions (DO NOT REVERT)
1. **Sequential Analysis:** Analysts (Bull/Bear) run sequentially in drafting/revision to avoid 429 RPM limits.
2. **Data Pre-fetching:** Data is fetched once in `workflow.py` and passed to agents as JSON to ensure consistency and minimize API calls.
3. **Agentic Reflection:** 2-iteration loop (Draft -> CIO Critique -> Revision -> Final Judgment).
4. **Resilient Parsing:** The `BacktestEngine` uses regex to extract JSON from LLM responses to handle markdown clutter.
5. **Backtest Mode:** Environment variable `BACKTEST_MODE=true` forces CIO to use `gpt-4o-mini` to preserve credits.

## 🚀 How to Resume
1. Run `.\venv\Scripts\activate` inside `Trading-Project`.
2. Run `python main.py` to launch the Gradio UI.
3. To continue development, see `PRD.md` for Stage 3 (Agent Customization/Refinement).
