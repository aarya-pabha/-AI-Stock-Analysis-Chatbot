# Institutional Dashboard V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the Gradio UI for production clarity, remove backtesting features, and prepare for Hugging Face deployment.

**Architecture:** Single-page Gradio Blocks UI with enhanced Markdown transformation of agent outputs and a new "Executive Summary" card.

**Tech Stack:** Gradio 6.0, Python 3.11, OpenBB, BeeAI.

---

### Task 1: Clean Up UI Architecture
**Files:**
- Modify: `src/ui/app.py`
- Modify: `main.py`

- [ ] **Step 1: Remove Backtest UI components**
Delete `run_backtest_ui` function and the "Institutional Backtest" tab from `create_ui`.
- [ ] **Step 2: Update `main.py`**
Remove any leftover references to backtesting if they exist in the entry point.
- [ ] **Step 3: Verify app still launches**
Run `python main.py` and confirm only the "Live Analysis" features remain.

### Task 2: Implement Markdown Transformation Layer
**Files:**
- Modify: `src/ui/app.py`

- [ ] **Step 1: Add `format_thesis` helper**
Write a utility function to convert `AnalystThesis` (or its raw iteration string) into structured Markdown bullets.
```python
def format_thesis(raw_text):
    # logic to parse catalysts/vulnerabilities from JSON-like strings or objects
    return formatted_markdown
```
- [ ] **Step 2: Add `format_summary` helper**
Write a utility to extract Recommendation, Price Target, and R:R from the `FinalReport` object into a summary card.

### Task 3: Refactor Layout & Visual Context
**Files:**
- Modify: `src/ui/app.py`

- [ ] **Step 1: Implement "Executive Summary" row**
Add a `gr.Markdown` area at the top of the results section that updates with the CIO's final decision.
- [ ] **Step 2: Add `gr.Examples`**
Provide users with one-click analysis for AAPL, NVDA, TSLA, and BTC.
- [ ] **Step 3: Update `run_analysis` yield logic**
Ensure the workflow yields the *formatted* Markdown instead of raw strings to the UI components.

### Task 4: Production Hardening & Deployment Prep
**Files:**
- Create: `Dockerfile`
- Modify: `requirements.txt`
- Modify: `.env.example`

- [ ] **Step 1: Update requirements**
Prune `requirements.txt` to the minimum set needed for the UI and Core logic.
- [ ] **Step 2: Create HF Dockerfile**
Standard Python 3.11 container with Gradio on port 7860.
- [ ] **Step 3: Add Image Cleanup tool**
Add a small utility to `src/ui/app.py` that deletes old charts from `data/` on startup or after analysis.

### Task 5: Final Validation
- [ ] **Step 1: Run local integration test**
Run a full analysis for "NVDA" and verify no JSON is visible in the UI.
- [ ] **Step 2: Check formatting integrity**
Ensure bullet points and headers render correctly in both Bull and Bear accordions.
- [ ] **Step 3: Commit all changes**
Final commit for V2 UI.
