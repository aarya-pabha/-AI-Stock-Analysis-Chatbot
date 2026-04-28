# Product Requirements Document (PRD): AI Stock Analysis Chatbot

## 1. Project Overview
**Name:** AI Stock Analysis Chatbot
**Goal:** Build a conversational AI system that allows users to input a US stock or ETF ticker and receive a highly scrutinized, research-backed trading recommendation (Buy/Sell/Hold) for both short-term (2-3 weeks) and long-term (6-12 months) horizons.
**Core Differentiator:** Instead of a single LLM guessing based on raw JSON, the system uses a **Multimodal Multi-Agent Council** with an "Agentic Reflection Loop," backed by deterministic quantitative math and strictly gated by market regime filters.

## 2. Architecture & Tech Stack
*   **Orchestration:** BeeAI (Enables stateful, cyclic multi-agent workflows and reflection loops).
*   **Agent Models:** Vision-Language Models (VLMs) like GPT-4o or Claude 3.5 Sonnet capable of multimodal reasoning (interpreting charts + data).
*   **Data Infrastructure:** OpenBB accessed via Model Context Protocol (MCP) for resilient, multi-source data (yfinance, SEC, options, insider data).
*   **Interface:** Gradio chat UI.

## 3. User Inputs & Context Enrichment
To avoid generic analysis and hallucinated assumptions, the system employs a Context Enrichment Gateway.

### Required Input
*   **Ticker (String):** The exact US stock or ETF symbol (e.g., `AAPL`, `SPY`).

### Optional Inputs (Personalization Layer)
If omitted, the system falls back to default assumptions and explicitly discloses them in the final output.
*   **Current Position:** None / Long / Short (Default: None). Shifts the debate from "Should we enter?" to "Should we manage/exit?"
*   **Risk Tolerance:** Conservative / Moderate / Aggressive (Default: Moderate). Adjusts the acceptable Risk/Reward (R:R) ratio (e.g., 3:1 vs 1.5:1) and volatility thresholds.
*   **Investment Horizon:** Short-Term / Long-Term / Both (Default: Both). Optimizes agent token usage by bypassing irrelevant analysis.

## 4. The Multi-Agent Council (Roles & Tools)

### Agent A: The Bull (Optimistic Analyst)
*   **Role:** Synthesize the strongest possible case for why the asset will increase in value.
*   **Tools (via MCP):**
    *   `get_multimodal_chart(ticker, timeframe)`: Generates and reads a `.png` candlestick chart with volume and moving averages.
    *   `get_momentum_indicators(ticker)`: Returns JSON of RSI, MACD, and Stochastic oscillators.
    *   `get_insider_buying(ticker)`: Fetches recent open-market purchases by executives.
    *   `get_growth_metrics(ticker)`: Fetches YoY Revenue and EPS growth rates.
    *   `get_analyst_upgrades(ticker)`: Fetches recent Wall Street price target increases.

### Agent B: The Bear (Pessimistic Analyst)
*   **Role:** Synthesize the strongest possible case for why the asset will decrease in value or why it is a value trap.
*   **Tools (via MCP):**
    *   `get_multimodal_chart(ticker, timeframe)`: Same visual chart analysis for resistance and breakdown patterns.
    *   `get_volatility_indicators(ticker)`: Returns JSON of Bollinger Bands and Average True Range (ATR).
    *   `get_insider_selling(ticker)`: Fetches recent dumps by executives.
    *   `get_short_interest_data(ticker)`: Checks the percentage of float shorted and days-to-cover.
    *   `get_risk_metrics(ticker)`: Fetches Debt-to-Equity ratio and declining profit margins.

### Agent C: The CIO / Risk Manager (The Judge)
*   **Role:** Evaluate the Bull and Bear theses, provide feedback for refinement, enforce hard quantitative rules, and synthesize the final output.
*   **Tools (via MCP & Deterministic Python):**
    *   `check_market_regime()`: Checks if SPY/QQQ > 200-day SMA. Penalizes Bull score in bear markets.
    *   `check_liquidity_gate(ticker)`: Fails the trade if Average Daily Volume (ADV) < 1,000,000 shares.
    *   `calculate_risk_reward(entry, atr_value, risk_tolerance)`: Deterministic Python script. Calculates exact Stop-Loss and Take-Profit targets based on ATR and user risk profile.
    *   `evaluate_reflection_delta(draft_1, draft_2)`: Tracks argument changes post-critique to finalize confidence scores.

## 5. Logic Flow & The Agentic Reflection Loop

1.  **User Request:** User provides ticker and optional parameters.
2.  **Data Generation:** MCP Server pulls data and generates the annotated `.png` chart.
3.  **Iteration 0 (Drafting):** The Bull and Bear VLMs independently analyze the chart and JSON, submitting Draft 1 of their arguments to the CIO.
4.  **Iteration 1 (The CIO's Critique):** The CIO reviews the drafts against deterministic data and user context, acting as the "Red Team" to provide specific feedback (e.g., flagging unconfirmed volume breakouts or missing options data).
5.  **Iteration 2 (The Revision):** Analysts revise their theses, either conceding points or pulling new data via tools to defend their stance.
6.  **Final Judgment:** The CIO terminates the loop, calculates the final Confidence Score, and runs deterministic math (`calculate_risk_reward`).
7.  **Output Generation:** The system returns a structured response including the Assumption Disclosure, Short-Term Signal, Long-Term Signal, Confidence Score, and Actionable Price Levels.

## 6. Backtesting Methodology (The FINSABER Standard)
To ensure the system generates actual Alpha and prevents LLM hallucination/data leakage, a rigorous backtesting harness will be implemented prior to V1 release:
1.  **Time-Capsule Integrity:** Backtests will strictly run on data post-dating the LLM's knowledge cutoff (e.g., Jan 2024 to Present). The MCP server will be restricted to feed historical point-in-time data (no live web searches during backtests).
2.  **Walk-Forward Rolling Windows:** Testing will occur in 3-month rolling blocks (e.g., Jan-Mar, roll to Feb-Apr) to prove the agents adapt to changing market regimes (Bull, Bear, Choppy).
3.  **Physical Execution Audit:** All CIO "Buy/Sell" signals will pass through a Python backtester (e.g., `Backtrader` or Magents) to apply realistic slippage and commission, verifying if the Risk/Reward targets were actually hit before the stop-loss.
4.  **Success Metrics:** The system must achieve a Sharpe Ratio > 1.2 and a Win Rate > 45% (profitable given the dynamic R:R) in out-of-sample testing to be validated for production.
