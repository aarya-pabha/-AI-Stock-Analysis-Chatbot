# AI Stock Analysis Chatbot

An institutional-grade, multi-agent system powered by Gemini 3.1, BeeAI, and OpenBB. Evaluates technicals, fundamentals, and strict quantitative regimes before issuing mathematically derived targets.

## Features
- **Multimodal Council**: Bull, Bear, and CIO agents debating with Gemini 3.1 Pro/Flash.
- **OpenBB Integration**: Real-time market data, momentum, volatility, and insider metrics.
- **Agentic Reflection Loop**: Agents revise and refine their thesis through a Red Team critique.
- **Deterministic Math Lab**: Generates exact Take-Profit and Stop-Loss based on ATR.

## Setup
1. Create a `.env` file with your `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) and `OPENBB_PAT`.
2. Run `python main.py` to start the Gradio app.
