# Design Spec: Institutional Dashboard V2 & HF Deployment

**Date:** 2026-05-15
**Status:** Approved
**Topic:** UI Refactoring and Deployment Optimization

## 1. Overview
The goal is to transition the AI Stock Analysis Chatbot from a developer-focused tool with backtesting capabilities to a clean, production-ready "Institutional Dashboard" suitable for deployment on Hugging Face Spaces.

## 2. Key Changes
- **Single-Page Focus:** Remove the "Institutional Backtest" tab to simplify the user journey.
- **Human-Readable Output:** Convert raw Pydantic/JSON outputs into structured Markdown.
- **Executive Summary:** Add a high-visibility card for the CIO's final decision.
- **Hugging Face Compatibility:** Optimize for free-tier hardware (2 vCPUs, 16GB RAM).

## 3. Architecture
- **UI Framework:** Gradio 6.0 (Blocks).
- **Transformation Layer:** Helper functions in `src/ui/app.py` to parse `AnalystThesis` and `FinalReport`.
- **State Management:** Retain `TradingState` for workflow orchestration but filter intermediate logs from the primary UI components.

## 4. UI Layout (Mockup)
- **Top Row:** 
    - Inputs (Ticker, Horizon, Risk) 
    - Examples (AAPL, NVDA, TSLA)
- **Second Row:**
    - Executive Summary Card (Decision, Price Target, Confidence)
- **Third Row (Side-by-Side):**
    - Visual Chart (Left)
    - Bull/Bear Accordions (Right - Final Iteration Only)
- **Bottom:** 
    - Raw Execution Logs (Collapsed by default)

## 5. Security & Deployment
- **Secrets:** Use HF Secrets for `OPENAI_API_KEY`, `GOOGLE_API_KEY`, and `OPENBB_PAT`.
- **Cleanup:** Implement image cleanup to prevent disk bloat on the HF Space.
