import pytest
from src.orchestration.schemas import UserContext
from src.agents.bull_agent import create_bull_agent
from src.agents.cio_agent import create_cio_agent

def test_agent_creation():
    context = UserContext(ticker="NVDA")
    
    bull = create_bull_agent(context)
    assert bull is not None
    assert bull._llm.model_id == "gemini-3.1-flash-lite-preview"
    
    cio = create_cio_agent(context)
    assert cio is not None
    assert cio._llm.model_id == "gemini-3.1-pro-preview"
