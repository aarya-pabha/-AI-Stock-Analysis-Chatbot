import gradio as gr
import os
import json
import glob
from pathlib import Path
from src.orchestration.schemas import UserContext, AnalystThesis, FinalReport
from src.orchestration.workflow import create_trading_workflow, TradingState
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

def cleanup_old_charts(ticker: str = None):
    """Deletes old *_chart.png files in the data/ directory. If ticker is provided, only deletes for that symbol."""
    data_dir = Path("data")
    if not data_dir.exists():
        return
        
    pattern = f"{ticker.upper()}_*_chart.png" if ticker else "*_chart.png"
    for f in data_dir.glob(pattern):
        try:
            f.unlink()
        except Exception:
            pass

def format_thesis(thesis_data: str) -> str:
    """Converts AnalystThesis into structured Markdown bullets."""
    if not thesis_data or str(thesis_data).strip().upper() == "N/A":
        return "N/A"
    
    try:
        # Agents return JSON strings based on expected_output=AnalystThesis
        data = json.loads(thesis_data)
        thesis = AnalystThesis(**data)
            
        vulns_list = getattr(thesis, 'key_vulnerabilities', []) or []
        vulns = "\n".join([f"* {v}" for v in vulns_list])
        
        return (
            f"### Thesis Statement\n"
            f"**Technical:** {thesis.technical_argument}\n\n"
            f"**Fundamental:** {thesis.fundamental_argument}\n\n"
            f"### Key Vulnerabilities\n"
            f"{vulns}\n\n"
            f"**Confidence Score:** {thesis.confidence_score}%"
        )
    except Exception:
        # Fallback to raw text if parsing fails (e.g. if agent didn't output JSON)
        return str(thesis_data)

def format_summary(report_data: str) -> str:
    """Extracts key metrics from FinalReport into a summary card."""
    if not report_data or str(report_data).strip().upper() == "N/A":
        return "N/A"

    try:
        data = json.loads(report_data)
        report = FinalReport(**data)
            
        math = report.actionable_math
        
        tp = f"${math.take_profit_price:.2f}" if math.take_profit_price is not None else "N/A"
        sl = f"${math.stop_loss_price:.2f}" if math.stop_loss_price is not None else "N/A"
        
        return (
            f"## 🏁 Final Judgment: {report.ticker}\n"
            f"**Recommendation:** {math.actionable_signal}\n\n"
            f"**Short-Term:** {report.short_term_signal} | **Long-Term:** {report.long_term_signal}\n\n"
            f"### 🎯 Price Targets & R:R\n"
            f"*   **Take Profit (Target):** {tp}\n"
            f"*   **Stop Loss:** {sl}\n"
            f"*   **Risk/Reward Ratio:** {math.risk_reward_ratio}\n\n"
            f"### 🧠 CIO Synthesis\n"
            f"{report.cio_synthesis}"
        )
    except Exception:
        return str(report_data)

async def run_analysis(ticker: str, position: str, risk: str, horizon: str):
    """
    Triggers the BeeAI Orchestration graph to run the Bull, Bear, and CIO agents.
    Yields intermediate states to the Gradio UI for real-time feedback.
    """
    if not ticker or ticker.strip() == "":
        yield "Error: Ticker cannot be empty.", None, None, None, None
        return

    ticker = ticker.strip().upper()
    
    # Clean up old charts for THIS ticker before starting a new analysis
    cleanup_old_charts(ticker)
    
    # Fetch current market price for math-lab accuracy
    import yfinance as yf
    try:
        tkr = yf.Ticker(ticker)
        # Try to get live price, fallback to last close from history
        curr_price = tkr.info.get("regularMarketPrice")
        
        if curr_price is None:
            hist = tkr.history(period="1d")
            if not hist.empty and 'Close' in hist.columns:
                curr_price = hist['Close'].iloc[-1]
            else:
                # Try 5d as a secondary fallback
                hist = tkr.history(period="5d")
                if not hist.empty and 'Close' in hist.columns:
                    curr_price = hist['Close'].iloc[-1]
        
        if curr_price is None or (hasattr(curr_price, 'empty') and curr_price.empty):
             raise ValueError(f"Could not retrieve a valid price for {ticker}")

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
        None, 
        "Awaiting execution...", 
        "Awaiting execution...", 
        "## 📋 Executive Summary\n*Awaiting execution...*"
    )
    
    try:
        # Create and run the workflow
        workflow = create_trading_workflow()
        
        # Step 1: Drafting
        yield (
            "Phase 1: Analysts are reviewing charts and fundamental data to draft initial theses...", 
            None, 
            "Awaiting execution...", 
            "Awaiting execution...", 
            "## 📋 Executive Summary\n*Awaiting execution...*"
        )
        response = await workflow.run(state)
        final_state = response.state
        
        # We assume workflow.run completes all steps automatically based on our routing.
        # So we just extract the final state.
        
        bull_draft_text = format_thesis(final_state.bull_draft or "N/A")
        bear_draft_text = format_thesis(final_state.bear_draft or "N/A")
        final_report_text = format_summary(final_state.final_report or "N/A")
        
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

def create_ui():
    """Builds the Gradio web interface."""
    # Clean up charts on startup
    cleanup_old_charts()
    
    with gr.Blocks(title="AI Stock Analysis Chatbot", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 📈 AI Stock Analysis Chatbot (Institutional V2)")
        gr.Markdown(
            "**Methodology:** Institutional-grade multi-agent stock analysis with bi-directional walk-forward backtesting (FINSABER Standard). "
            "Combining Bull/Bear dialectics with CIO synthesis and math-lab risk modeling."
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 1. Analysis Context")
                ticker_input = gr.Textbox(label="Ticker Symbol", placeholder="e.g. AAPL, NVDA, SPY")
                position_input = gr.Radio(["None", "Long", "Short"], label="Current Position", value="None")
                risk_input = gr.Radio(["Conservative", "Moderate", "Aggressive"], label="Risk Tolerance", value="Moderate")
                horizon_input = gr.Radio(["Short-Term", "Long-Term", "Both"], label="Investment Horizon", value="Both")
                
                submit_btn = gr.Button("Run Institutional Analysis", variant="primary")
                
            with gr.Column(scale=1):
                gr.Markdown("### ⚡ Quick Presets")
                gr.Examples(
                    examples=[
                        ["AAPL", "None", "Moderate", "Both"],
                        ["NVDA", "Long", "Aggressive", "Long-Term"],
                        ["TSLA", "None", "Aggressive", "Short-Term"],
                        ["BTC-USD", "None", "Moderate", "Both"]
                    ],
                    inputs=[ticker_input, position_input, risk_input, horizon_input],
                    label="Institutional Presets"
                )

        # Row 2: Executive Summary (CIO Judgment)
        final_output = gr.Markdown("## 📋 Executive Summary\n*Awaiting execution...*")
        
        # Row 3: Visuals + Theses
        with gr.Row():
            with gr.Column(scale=2):
                chart_output = gr.Image(label="Visual Context (VLMs)", type="filepath")
            with gr.Column(scale=1):
                with gr.Accordion("Bull Agent Thesis", open=True):
                    bull_output = gr.Markdown("Awaiting execution...")
                with gr.Accordion("Bear Agent Thesis", open=True):
                    bear_output = gr.Markdown("Awaiting execution...")
        
        # Footer: Execution Logs
        with gr.Accordion("Execution Logs", open=False):
            status_box = gr.Markdown("Ready.")

        # Wire up Live btn
        submit_btn.click(
            fn=run_analysis,
            inputs=[ticker_input, position_input, risk_input, horizon_input],
            outputs=[status_box, chart_output, bull_output, bear_output, final_output]
        )
        
    return app
