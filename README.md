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
flowchart TD
    %% Global Entry
    User([User Query]) --> Orchestrator{BeeAI Orchestrator}

    %% Shared State & Tools
    subgraph Data_Layer [Data & Tooling Layer]
        direction LR
        MCP[OpenBB / yfinance] <--> VLM[VLM Chart Generator]
    end

    Orchestrator --> Data_Layer

    %% Drafting Phase
    subgraph Analysts [Phase 1 & 3: Drafting & Revision]
        direction LR
        Bull[<b>Bull Agent</b><br/>Momentum & Growth] 
        Bear[<b>Bear Agent</b><br/>Volatility & Risk]
    end

    Data_Layer ==> Analysts

    %% Reflection Phase
    subgraph Judgment [Phase 2 & 4: Critique & Final Judgment]
        direction TB
        CIO{<b>CIO / Risk Manager</b><br/>Regime Check & Liquidity}
        Math[[ATR Math Lab]]
    end

    %% The Core Loop
    Analysts == "Submit Drafts" ==> CIO
    CIO -. "Red Team Critique<br/>(Identify Vulnerabilities)" .-> Analysts
    
    %% Final Output
    CIO == "Approve & Apply Math" ==> Math
    Math ==> Final([<b>Final Institutional Report</b><br/>TP, SL, Confidence, R:R])

    %% Styling
    classDef orchestrator fill:#e3f2fd,stroke:#0288d1,stroke-width:2px;
    classDef bull fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef bear fill:#ffebee,stroke:#c62828,stroke-width:2px;
    classDef judge fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef tools fill:#f3e5f5,stroke:#8e24aa,stroke-width:1px;
    classDef final fill:#e0f7fa,stroke:#0277bd,stroke-width:2px;

    class Orchestrator orchestrator;
    class Bull bull;
    class Bear bear;
    class CIO judge;
    class MCP,VLM,Math tools;
    class Final final;
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
