import pytest
from pydantic import ValidationError
from src.orchestration.schemas import UserContext, AnalystThesis, FinalReport, ActionableMath

def test_user_context_validation():
    # Valid input
    ctx = UserContext(ticker="AAPL", current_position="Long", risk_tolerance="Aggressive", next_open_price=150.25)
    assert ctx.ticker == "AAPL"
    assert ctx.risk_tolerance == "Aggressive"
    assert ctx.next_open_price == 150.25
    
    # Invalid ticker (missing)
    with pytest.raises(ValidationError):
        UserContext()

def test_analyst_thesis_validation():
    # Valid
    thesis = AnalystThesis(
        technical_argument="Strong breakout",
        fundamental_argument="High growth",
        confidence_score=85,
        key_vulnerabilities=["Macro risk"]
    )
    assert thesis.confidence_score == 85

def test_final_report_validation():
    ctx = UserContext(ticker="AAPL", next_open_price=150.50)
    math = ActionableMath(
        direction="Long",
        entry_price=150.0,
        stop_loss_price=140.0,
        take_profit_price=170.0,
        risk_reward_ratio="2:1",
        actionable_signal="Buy at 150"
    )
    report = FinalReport(
        ticker="AAPL",
        assumptions_used=ctx,
        short_term_signal="Buy",
        long_term_signal="Hold",
        cio_synthesis="Debate resolved",
        actionable_math=math
    )
    assert report.ticker == "AAPL"
    assert report.actionable_math.direction == "Long"
