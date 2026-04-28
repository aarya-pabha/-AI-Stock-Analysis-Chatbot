import pytest
from pydantic import ValidationError
from src.orchestration.schemas import UserContext, AnalystThesis, FinalReport

def test_user_context_validation():
    # Valid input
    ctx = UserContext(ticker="AAPL", current_position="Long", risk_tolerance="Aggressive")
    assert ctx.ticker == "AAPL"
    assert ctx.risk_tolerance == "Aggressive"
    
    # Invalid ticker (missing)
    with pytest.raises(ValidationError):
        UserContext()
    
    # Invalid enum value
    with pytest.raises(ValidationError):
        UserContext(ticker="AAPL", risk_tolerance="Insane")

def test_analyst_thesis_validation():
    # Valid
    thesis = AnalystThesis(
        agent_role="Bull",
        technical_argument="Strong breakout",
        fundamental_argument="High growth",
        confidence_score=85,
        key_vulnerabilities=["Macro risk"]
    )
    assert thesis.confidence_score == 85
    
    # Invalid score
    with pytest.raises(ValidationError):
        AnalystThesis(
            agent_role="Bull",
            technical_argument="X",
            fundamental_argument="Y",
            confidence_score=150,
            key_vulnerabilities=[]
        )

def test_final_report_validation():
    ctx = UserContext(ticker="AAPL")
    report = FinalReport(
        ticker="AAPL",
        assumptions_used=ctx,
        short_term_signal="Buy",
        long_term_signal="Hold",
        cio_synthesis="Debate resolved",
        actionable_math={"entry": 150}
    )
    assert report.ticker == "AAPL"
    assert report.assumptions_used.ticker == "AAPL"
