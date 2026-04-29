import gradio as gr
import asyncio
import os
import json
from src.orchestration.schemas import UserContext
from src.orchestration.workflow import create_trading_workflow, TradingState
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

async def run_analysis(ticker: str, position: str, risk: str, horizon: str):
    """
    Triggers the BeeAI Orchestration graph to run the Bull, Bear, and CIO agents.
    Yields intermediate states to the Gradio UI for real-time feedback.
    """
    if not ticker or ticker.strip() == "":
        yield "Error: Ticker cannot be empty.", None, None, None, None
        return

    ticker = ticker.strip().upper()
    
    # Fetch current market price for math-lab accuracy
    import yfinance as yf
    try:
        tkr = yf.Ticker(ticker)
        # Try to get live price, fallback to last close
        curr_price = tkr.info.get("regularMarketPrice") or tkr.history(period="1d")['Close'].iloc[-1]
    except Exception as e:
        yield f"Error fetching price for {ticker}: {e}", None, None, None, None
        return

    # 1. Build the UserContext from the UI inputs
    context = UserContext(
        ticker=ticker,
        current_position=position,
        risk_tolerance=risk,
        investment_horizon=horizon,
        next_open_price=round(float(curr_price), 2)
    )
    
    # Initialize state
    state = TradingState(context=context)
    
    # Yield initial loading message
    yield (
        f"**System initialized.**\nFetching data and charts for {ticker}...\nOrchestrating Bull and Bear agents (Iteration 0)...",
        None, None, None, None
    )
    
    try:
        # Create and run the workflow
        workflow = create_trading_workflow()
        
        # We manually step through the workflow to yield intermediate UI updates
        # Alternatively, we could just run `await workflow.run(state)`
        
        # Step 1: Drafting
        yield "Phase 1: Analysts are reviewing charts and fundamental data to draft initial theses...", None, None, None, None
        response = await workflow.run(state)
        final_state = response.state
        
        # We assume workflow.run completes all steps automatically based on our routing.
        # So we just extract the final state.
        
        bull_draft_text = final_state.bull_draft or "N/A"
        bear_draft_text = final_state.bear_draft or "N/A"
        cio_critique_text = final_state.cio_critique or "N/A"
        final_report_text = final_state.final_report or "N/A"
        
        # Format the output elegantly
        status_msg = f"✅ **Analysis Complete for {ticker}**"
        
        # Attempt to load the image if it exists (from the tools directory)
        # Note: In a production app we'd pass the path strictly from the tool output
        chart_path = f"data/{ticker}_daily_chart.png"
        image_output = chart_path if os.path.exists(chart_path) else None

        yield (
            status_msg,
            image_output,
            bull_draft_text,
            bear_draft_text,
            final_report_text
        )
        
    except Exception as e:
        yield f"**Error during execution:** {str(e)}", None, None, None, None

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

def create_ui():
    """Builds the Gradio web interface."""
    
    with gr.Blocks(title="AI Stock Analysis Chatbot", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 📈 AI Stock Analysis Chatbot (2026 SOTA)")
        
        with gr.Tabs():
            with gr.Tab("Live Analysis"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 1. Context Enrichment Gateway")
                        ticker_input = gr.Textbox(label="Ticker Symbol", placeholder="e.g. AAPL, NVDA, SPY")
                        position_input = gr.Radio(["None", "Long", "Short"], label="Your Current Position", value="None")
                        risk_input = gr.Radio(["Conservative", "Moderate", "Aggressive"], label="Risk Tolerance", value="Moderate")
                        horizon_input = gr.Radio(["Short-Term", "Long-Term", "Both"], label="Investment Horizon", value="Both")
                        
                        submit_btn = gr.Button("Run Institutional Analysis", variant="primary")
                        status_box = gr.Markdown("Ready.")
                        
                    with gr.Column(scale=2):
                        gr.Markdown("### 2. Visual Context")
                        chart_output = gr.Image(label="Generated Multimodal Chart (Analyzed by VLMs)", type="filepath")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 3. Agentic Debate (Iteration 0)")
                        with gr.Accordion("Bull Agent Thesis", open=False):
                            bull_output = gr.Markdown("Awaiting execution...")
                        with gr.Accordion("Bear Agent Thesis", open=False):
                            bear_output = gr.Markdown("Awaiting execution...")
                    
                    with gr.Column():
                        gr.Markdown("### 4. CIO Final Judgment (Iteration 2)")
                        final_output = gr.Markdown("Awaiting execution...")

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

        # Wire up Live btn
        submit_btn.click(
            fn=run_analysis,
            inputs=[ticker_input, position_input, risk_input, horizon_input],
            outputs=[status_box, chart_output, bull_output, bear_output, final_output]
        )
        
        # Wire up Backtest btn
        bt_btn.click(
            fn=run_backtest_ui,
            inputs=[bt_ticker, bt_start, bt_end, bt_interval],
            outputs=[bt_summary, bt_results]
        )
        
    return app
