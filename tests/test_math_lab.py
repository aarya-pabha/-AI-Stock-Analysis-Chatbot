import pytest
from src.tools.math_lab import calculate_risk_reward

def test_conservative_risk_reward():
    # Conservative should have 3:1 R:R
    res = calculate_risk_reward(100.0, 10.0, "Conservative")
    assert res["stop_loss_price"] == 90.0
    assert res["take_profit_price"] == 130.0
    assert res["risk_reward_ratio"] == "3.0:1"

def test_aggressive_risk_reward():
    # Aggressive should have 1.5:1 R:R
    res = calculate_risk_reward(100.0, 10.0, "Aggressive")
    assert res["stop_loss_price"] == 80.0
    assert res["take_profit_price"] == 130.0
    assert res["risk_reward_ratio"] == "1.5:1"

def test_short_direction_math():
    # Moderate Short: ATR 10. Multiplier 1.5 -> Risk 15. Reward 30.
    res = calculate_risk_reward(100.0, 10.0, "Moderate", direction="Short")
    assert res["direction"] == "Short"
    assert res["stop_loss_price"] == 115.0  # Entry + Risk
    assert res["take_profit_price"] == 70.0  # Entry - Reward
    assert res["risk_reward_ratio"] == "2.0:1"

def test_invalid_risk_defaults_to_moderate():
    res = calculate_risk_reward(100.0, 10.0, "YOLO")
    assert res["risk_tolerance"] == "Moderate"
    assert res["risk_reward_ratio"] == "2.0:1"
