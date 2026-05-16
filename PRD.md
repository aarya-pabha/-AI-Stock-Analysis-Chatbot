# Product Requirements Document (PRD): AI Stock Analysis Chatbot

## 1. Project Overview
**Name:** AI Stock Analysis Chatbot
**Goal:** Build a conversational AI system that allows users to input a US stock or ETF ticker and receive a highly scrutinized, research-backed trading recommendation (Buy/Sell/Hold) for both short-term (2-3 weeks) and long-term (6-12 months) horizons.
**Core Differentiator:** Instead of a single LLM guessing based on raw JSON, the system uses a **Multimodal Multi-Agent Council** with an "Agentic Reflection Loop," backed by deterministic quantitative math and strictly gated by market regime filters.

## 2. Architecture & Tech Stack (VERIFIED)
*   **Orchestration:** BeeAI Framework (Stateful Workflow).
*   **Workflow Pattern:** 4-Step Cyclic Reflection (Drafting -> Critique -> Revision -> Judgment).
*   **Agent Models:** 
    *   **CIO Judge:** OpenAI `gpt-4o` (High reasoning & tool accuracy).
    *   **Analysts:** OpenAI `gpt-4o-mini` (Cost-effective drafting & multimodality).
*   **Interface:** Gradio 5.50.0 (Custom Dashboard V2).
*   **Data Infrastructure:** OpenBB v4 (Fundamental/Macro) + yfinance (Price/Execution).

## 3. User Inputs & Context Enrichment
To avoid generic analysis and hallucinated assumptions, the system employs a Context Enrichment Gateway.

### Required Input
*   **Ticker (String):** The exact US stock or ETF symbol (e.g., `AAPL`, `SPY`).

### Personalization Layer
*   **Current Position:** None / Long / Short.
*   **Risk Tolerance:** Conservative / Moderate / Aggressive.
*   **Investment Horizon:** Short-Term / Long-Term / Both.

## 4. The Multi-Agent Council (Roles & Tools)

### Agent A: The Bull (Optimistic Analyst)
*   **Role:** Synthesize the strongest possible case for why the asset will increase in value.
*   **Tools:** Momentum indicators, Insider buying, Growth metrics, and VLM Chart Analysis.

### Agent B: The Bear (Pessimistic Analyst)
*   **Role:** Synthesize the strongest possible case for why the asset will decrease in value or why it is a value trap.
*   **Tools:** Volatility indicators, Insider selling, Short interest data, and VLM Chart Analysis.

### Agent C: The CIO / Risk Manager (The Judge)
*   **Role:** Evaluate analyst theses, act as the Red Team (Critique), enforce hard quantitative rules, and synthesize the final output.
*   **Tools:** Market Regime Check (200 SMA), Liquidity Gate, and ATR-based Math Lab (SL/TP calculation).

## 5. Logic Flow & The Agentic Reflection Loop

1.  **Phase 1: Drafting (Iteration 0):** Bull and Bear independently analyze chart `.png` and JSON data packet.
2.  **Phase 2: Critique (Iteration 1):** CIO reviews drafts, identifies vulnerabilities, and issues Red Team feedback.
3.  **Phase 3: Revision (Iteration 2):** Analysts revise their theses based on CIO feedback.
4.  **Phase 4: Judgment:** CIO enforces quantitative guardrails and outputs a pydantic-validated `FinalReport`.

## 6. Backtesting Methodology (The FINSABER Standard) - COMPLETED
1.  **Walk-Forward Audit:** Signals verified against historical next-day open prices.
2.  **Stateful Position Management:** Tracks active trades to prevent overlap and simulate realistic portfolio friction.
3.  **Point-in-Time Integrity:** Gated tools ensure zero data leakage during simulation.

## 7. Development Roadmap Status
*   **Stage 1-4:** (Core Logic & Agents) - **DONE**.
*   **Stage 5:** (Institutional UI & V2 Dashboard) - **DONE**.
*   **Stage 6:** (Portfolio Optimization / Live Brokerage APIs) - **PLANNED**.

## 8. Safety & Compliance
*   **Disclaimer:** Automated disclosure that the tool is for research/education only.
*   **Data Protection:** `.env` and sensitive PATs are gapped from the codebase via `.gitignore`.
