from typing import Dict, Any, Literal

def calculate_risk_reward(entry_price: float, atr_value: float, risk_tolerance: str = "Moderate", direction: Literal["Long", "Short"] = "Long") -> Dict[str, Any]:
    """
    Deterministic Python script that calculates exact Stop-Loss and Take-Profit targets 
    based on Average True Range (ATR) and user risk tolerance for both Long and Short positions.
    """
    # Multipliers for Stop-Loss (Risk) and Take-Profit (Reward)
    if risk_tolerance not in ["Conservative", "Moderate", "Aggressive"]:
        risk_tolerance = "Moderate"
        
    if risk_tolerance == "Conservative":
        atr_multiplier = 1.0  # Tighter Stop
        reward_multiplier = 3.0  # Require higher R:R
    elif risk_tolerance == "Aggressive":
        atr_multiplier = 2.0  # Wider Stop
        reward_multiplier = 1.5  # Lower R:R threshold
    else:  # Moderate
        atr_multiplier = 1.5
        reward_multiplier = 2.0

    risk_amount = atr_value * atr_multiplier
    reward_amount = risk_amount * reward_multiplier

    if direction == "Long":
        stop_loss_price = round(entry_price - risk_amount, 2)
        take_profit_price = round(entry_price + reward_amount, 2)
        actual_rr = round((take_profit_price - entry_price) / (entry_price - stop_loss_price), 1) if entry_price > stop_loss_price else 0
        actionable_signal = f"LONG: Stop-Loss at ${stop_loss_price}. Target at ${take_profit_price}. R:R is {actual_rr}:1."
    else: # Short
        stop_loss_price = round(entry_price + risk_amount, 2)
        take_profit_price = round(entry_price - reward_amount, 2)
        actual_rr = round((entry_price - take_profit_price) / (stop_loss_price - entry_price), 1) if stop_loss_price > entry_price else 0
        actionable_signal = f"SHORT: Stop-Loss at ${stop_loss_price}. Target at ${take_profit_price}. R:R is {actual_rr}:1."

    return {
        "direction": direction,
        "entry_price": entry_price,
        "stop_loss_price": stop_loss_price,
        "take_profit_price": take_profit_price,
        "risk_tolerance": risk_tolerance,
        "risk_reward_ratio": f"{actual_rr}:1",
        "actionable_signal": actionable_signal
    }

if __name__ == "__main__":
    # Test
    print("Long Test:", calculate_risk_reward(135.0, 5.5, "Moderate", "Long"))
    print("Short Test:", calculate_risk_reward(135.0, 5.5, "Moderate", "Short"))
