# Product Requirements Document (PRD): AI Stock Analysis Chatbot

## 1. Project Overview
**Name:** AI Stock Analysis Chatbot (V1.0)
**Goal:** Build a conversational AI system that allows users to input a US stock or ETF ticker and receive a highly scrutinized, research-backed trading recommendation (Buy/Sell/Hold) for both short-term (2-3 weeks) and long-term (6-12 months) horizons.
**Core Differentiator:** Instead of a single LLM guessing based on raw JSON, the system uses a **Multimodal Multi-Agent Council** with an "Agentic Reflection Loop," backed by deterministic quantitative math and strictly gated by market regime filters.

## 2. Architecture & Tech Stack (VERIFIED)
*   **Orchestration:** BeeAI Framework (Stateful Workflow).
*   **Workflow Pattern:** 4-Step Cyclic Reflection (Drafting -> Critique -> Revision -> Judgment).
*   **Agent Models:** 
    *   **CIO Judge:** OpenAI `gpt-4o` (High reasoning & tool accuracy).
    *   **Analysts:** OpenAI `gpt-4o-mini` (Cost-effective drafting & multimodality).
*   **Interface:** Gradio 5.50.0 (Institutional Dashboard V2).
*   **Data Infrastructure:** OpenBB v4 (Fundamental/Macro) + yfinance (Price/Execution).

## 3. User Inputs & Context Enrichment
To avoid generic analysis and hallucinated assumptions, the system employs a Context Enrichment Gateway.

### Required Input
*   **Ticker (String):** The exact US stock or ETF symbol (e.g., `AAPL`, `SPY`).

### Personalization Layer
*   **Current Position:** None / Long / Short (Shifts debate from Entry to Management).
*   **Risk Tolerance:** Conservative / Moderate / Aggressive (Adjusts ATR-based R:R thresholds).
*   **Investment Horizon:** Short-Term / Long-Term / Both (Optimizes data windowing).

## 4. Multi-Agent Council: Tool Mapping (AS BUILT)

### Agent A: The Bull (Optimistic Analyst)
*   **Role:** Construct the strongest possible data-backed thesis for upside.
*   **Assigned Tools:**
    - `get_multimodal_chart`: Visual VLM analysis of candlestick patterns.
    - `get_momentum_indicators`: RSI, MACD, and Stochastic JSON metrics.
    - `get_growth_metrics`: YoY Revenue and EPS growth rates.
    - `get_insider_buying`: Recent open-market executive purchases.
    - `get_analyst_upgrades`: Price target increases from major banks.

### Agent B: The Bear (Pessimistic Analyst)
*   **Role:** Identify value traps, technical breakdowns, and fundamental risks.
*   **Assigned Tools:**
    - `get_multimodal_chart`: Visual VLM analysis for resistance/breakdown zones.
    - `get_volatility_indicators`: Bollinger Bands and ATR context.
    - `get_risk_metrics`: Debt-to-Equity and declining margin analysis.
    - `get_insider_selling`: Recent executive dumping/liquidation.
    - `get_short_interest_data`: Float short percentage and days-to-cover.

### Agent C: The CIO / Risk Manager (The Judge)
*   **Role:** Referee the Bull/Bear debate, act as the Red Team, and enforce math guardrails.
*   **Assigned Tools:**
    - `check_market_regime`: Hard filter for SPY/QQQ 200-day SMA alignment.
    - `check_liquidity_gate`: Veto trade if Daily Volume < 1M shares.
    - `calculate_risk_reward`: Deterministic ATR math for exact SL and TP targets.

## 5. Logic Flow & Reflection Loop
The system follows a strict state-managed sequence in `src/orchestration/workflow.py`:
1.  **Phase 1: Drafting (Iteration 0):** Analysts pull data and submit their initial `AnalystThesis`.
2.  **Phase 2: Critique (Iteration 1):** CIO attacks the vulnerabilities and provides revision feedback.
3.  **Phase 3: Revision (Iteration 2):** Analysts revise their arguments based on the CIO's Red Team findings.
4.  **Phase 4: Judgment:** CIO executes quantitative rules and outputs the validated `FinalReport`.

## 6. Backtesting Methodology (The FINSABER Standard)
1.  **Walk-Forward Audit:** Verified against historical **Next-Day Open** prices.
2.  **Stateful Position Management:** Tracks active trades to prevent "analysis overlap."
3.  **Point-in-Time Integrity:** Hard-gated tools ensure zero data leakage from future price action.

## 7. Development Status
*   **Current State:** V1.0 COMPLETE (Stage 1-5 finished).
*   **Roadmap:** Stage 6 (Live Brokerage APIs / Portfolio Optimization).
