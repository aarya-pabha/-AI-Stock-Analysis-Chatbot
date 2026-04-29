# Project Context: AI Stock Analysis Chatbot (V1.0 Finished)

## 🎯 Current Status
**Phase:** Stage 5 (Final UI & Institutional Integration) COMPLETE.
**Goal:** Institutional-grade multi-agent stock analysis with bi-directional walk-forward backtesting (FINSABER Standard).

## 🛠️ Tech Stack & Configuration
- **Orchestration:** BeeAI Framework (Stateful Workflow).
- **LLM Models:** 
  - CIO Judge: `openai:gpt-4o` (High-quality reasoning & tool calling)
  - Analysts: `openai:gpt-4o-mini` (Cost-effective drafting)
- **Data:** OpenBB v4 (Technical + Fundamentals) + yfinance (OHLCV & Real-time).
- **Vision:** `mplfinance` generating `.png` charts for VLM analysis.

## 🧠 Core Architectural Decisions (DO NOT REVERT)
1. **Bi-Directional Engine:** Supports both "Long" and "Short" signals with inverted ATR math.
2. **Realistic Execution:** Trades are simulated using the **Next-Day Market Open** following a signal to prevent data leakage.
3. **Hardened Personas:** Bull/Bear analysts are strictly constrained to their optimistic/pessimistic roles to ensure maximum council friction.
4. **Anti-Groupthink Logic:** CIO is instructed to prioritize quantitative math (R:R) over analyst caution during Bull Market regimes.
5. **Stateful Position Tracking:** `BacktestEngine` tracks active trades and locks out new analysis until the current position closes.
6. **Resilient Fundamentals:** Tools return neutral warnings instead of `null` to prevent bearish bias from missing historical data.

## 🚀 How to Resume
1. Run `.\venv\Scripts\activate`.
2. Run `python main.py` to launch the Gradio UI.
3. Use the **Institutional Backtest** tab to verify Alpha with walk-forward audits.
4. Future Work: Stage 6 (Portfolio Optimization / Live Brokerage APIs).
