# UI Architecture Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the legacy backtesting UI components from the application to prepare for the Institutional Dashboard V2 refactor.

**Architecture:** Surgical removal of the `run_backtest_ui` function and the associated Gradio Tab and event handlers in `src/ui/app.py`.

**Tech Stack:** Python, Gradio

---

### Task 1: Cleanup `src/ui/app.py`

**Files:**
- Modify: `src/ui/app.py`

- [ ] **Step 1: Remove `run_backtest_ui` function**

Delete the following function and its docstring:
```python
async def run_backtest_ui(ticker: str, start_date: str, end_date: str, interval: int):
    """Bridge between Gradio and the BacktestEngine with incremental updates."""
    from src.orchestration.backtest_engine import BacktestEngine
    import pandas as pd
    
    if not ticker or not start_date or not end_date:
        yield "Error: Please provide ticker and date range.", None
        return
        
    engine = BacktestEngine(ticker.upper(), start_date, end_date, interval_days=int(interval))
    all_trades = []
    
    yield f"🚀 Initializing bi-directional backtest for {ticker}...", None
    
    # engine.run() is an async generator yielding status, trades, and summary
    async for result in engine.run():
        if "summary" in result:
            s = result["summary"]
            final_summary = f"""
            ### ✅ Backtest Complete: {ticker}
            - **Total Trades:** {s['total_trades']}
            - **Win Rate:** {s['win_rate']}%
            - **Total PnL:** {s['total_pnl_pct']}%
            - **Sharpe Ratio:** {s['sharpe_ratio']}
            - **Simulation Window:** {s['start_date']} to {s['end_date']}
            """
            yield final_summary, pd.DataFrame(all_trades)
            return

        if "status" in result:
            yield f"⏳ **Status:** {result['status']}", pd.DataFrame(all_trades)
            continue
            
        # It's a trade result
        all_trades.append(result)
        df = pd.DataFrame(all_trades)
        
        # Display the most recent trade in the status
        last = all_trades[-1]
        msg = f"🔄 **Trade {len(all_trades)}:** {last['date']} | {last['direction']} at ${last['entry']} | Outcome: {last['outcome']} ({last['pnl_pct']}%)"
        yield msg, df

    if not all_trades:
        yield "Simulation complete. No trades were triggered during this period.", None
```

- [ ] **Step 2: Remove the "Institutional Backtest" Tab**

Delete the `with gr.Tab("Institutional Backtest (FINSABER)"):` block and its contents:
```python
            with gr.Tab("Institutional Backtest (FINSABER)"):
                gr.Markdown("Test the council's alpha generation using historical point-in-time data.")
                with gr.Row():
                    bt_ticker = gr.Textbox(label="Ticker", value="AAPL")
                    bt_start = gr.Textbox(label="Start Date", value="2025-01-01")
                    bt_end = gr.Textbox(label="End Date", value="2025-03-31")
                    bt_interval = gr.Slider(minimum=1, maximum=30, value=7, step=1, label="Analysis Interval (Days)")
                bt_btn = gr.Button("Execute Walk-Forward Simulation", variant="primary")
                bt_summary = gr.Markdown("No backtest data.")
                bt_results = gr.Dataframe(label="Trade Log")
```

- [ ] **Step 3: Remove Backtest event handler**

Delete the event wire-up for the backtest button:
```python
        # Wire up Backtest btn
        bt_btn.click(
            fn=run_backtest_ui,
            inputs=[bt_ticker, bt_start, bt_end, bt_interval],
            outputs=[bt_summary, bt_results]
        )
```

- [ ] **Step 4: Commit cleanup**

```bash
git add src/ui/app.py
git commit -m "refactor(ui): remove backtest components from app.py"
```

### Task 2: Verify `main.py`

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Check for backtest references**

Review `main.py` to ensure no backtesting-specific logic or imports remain. Based on initial inspection, it only calls `create_ui()`, which is fine. If any logic exists, remove it.

- [ ] **Step 2: Commit if changed**

```bash
git add main.py
git commit -m "refactor(ui): clean up main.py references"
```

### Task 3: Verification

- [ ] **Step 1: Run the application**

Run: `python main.py`
Wait for the Gradio link to appear (usually `http://127.0.0.1:7860`). Since I cannot access the browser, I will check if the script starts correctly without errors.

- [ ] **Step 2: Verify console output**

Ensure no import errors or runtime errors related to missing `run_backtest_ui`.

---
