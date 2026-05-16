# 📈 AI Stock Analysis Chatbot (V1.0)

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/aarya-pabha/AI-Stock-Analysis-Chatbot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)

**Institutional-grade multi-agent stock analysis with FINSABER backtesting.** Powered by Gemini 3.1, BeeAI, and OpenBB, this engine simulates a professional trading floor where AI analysts debate and refine their thesis through a cyclic reflection loop before issuing mathematically-backed signals.

---

## ✨ Highlights
- 🧠 **Agentic Reflection Loop**: A multi-step workflow where Bull and Bear analysts are critiqued and revised by a CIO.
- 📉 **Bi-Directional Signal Engine**: Supports Long/Short equity signals with automated ATR risk management.
- 🧪 **FINSABER Backtesting**: Verifies signals against next-day open prices with point-in-time fundamental data gating.
- 👁️ **Multimodal Intelligence**: Analysts "see" charts via integrated Vision-Language Models (GPT-4o).
- 🤖 **Agent-Ready Architecture**: Built for AI coding agents with structured `GEMINI.md` protocols.

---

## 🏗️ Architecture: The Council Flow
The system utilizes a stateful **BeeAI Workflow** to orchestrate specialized agents, each with dedicated Python toolsets.

```mermaid
graph TD
    %% Global Entry
    User([User Query]) --> Orch{BeeAI Orchestrator}
    
    %% Tool Gating
    Orch --> Tools[(Market Data: OpenBB, yfinance, VLM)]
    
    %% Agentic Reflection Loop
    subgraph Loop [Council Reflection & Decision Loop]
        direction TB
        
        Tools -.-> Bull
        Tools -.-> Bear
        
        Bull[<b>Bull Agent</b><br/><i>Growth & Momentum Tools</i>] -- "Initial Thesis" --> CIO
        Bear[<b>Bear Agent</b><br/><i>Risk & Volatility Tools</i>] -- "Initial Thesis" --> CIO
        
        CIO{<b>CIO Judge</b><br/><i>Regime & Math Lab</i>} -- "Red Team Critique" --> Bull
        CIO -- "Red Team Critique" --> Bear
        
        Bull -. "Revised Thesis" .-> CIO
        Bear -. "Revised Thesis" .-> CIO
    end
    
    %% Final Output
    Orch --> Loop
    CIO --> Final[/<b>Final Institutional Report</b><br/><i>TP, SL, Confidence, R:R</i>/]
    
    %% Visual Styling
    style CIO fill:#f96,stroke:#333,stroke-width:2px
    style Bull fill:#dfd,stroke:#333
    style Bear fill:#fdd,stroke:#333
    style Tools fill:#f0f0f0,stroke:#333
    style Final fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style User fill:#e8f5e9,stroke:#2e7d32
```

---

## 🛠️ Quick Start

### 1. Prerequisites
- Python 3.11+
- OpenAI API Key (for GPT-4o Orchestration)
- OpenBB Personal Access Token (PAT)

### 2. Installation
```bash
git clone https://github.com/aarya-pabha/-AI-Stock-Analysis-Chatbot.git
cd -AI-Stock-Analysis-Chatbot
python -m venv venv
.\venv\Scripts\activate  # Unix: source venv/bin/activate
pip install -r requirements.txt
```

### 3. Launch Institutional Dashboard
```bash
python main.py
```

---

## 📊 Technical Standards
- **Reflective Loop**: Steps are strictly state-managed: `Drafting` -> `Critique` -> `Revision` -> `Judgment`.
- **Math Lab**: Generates exact ATR-based Stop-Loss (SL) and Take-Profit (TP) levels.
- **Execution Reality**: Backtests simulate execution at the **Next-Day Market Open** to prevent data leakage.

---

## 🤖 AI Agent Integration
This repository is optimized for **AI-Assisted Development**. 
- **Instructions**: See [GEMINI.md](./GEMINI.md) for tool schemas and architectural constraints.
- **Project Context**: AI coding agents can use `MEMORY.md` to track implementation history.

---

## 🤝 Contributing
Contributions are welcome! See our `PRD.md` for technical specifications and the Stage 6 Roadmap (Live Brokerage Integration).

---
*Disclaimer: This tool is for educational and research purposes only. Trading stocks involves significant risk.*
