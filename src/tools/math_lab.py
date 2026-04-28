from typing import Dict, Any

def calculate_risk_reward(entry_price: float, atr_value: float, risk_tolerance: str = "Moderate") -> Dict[str, Any]:
    """
    Deterministic Python script that calculates exact Stop-Loss and Take-Profit targets 
    based on the Average True Range (ATR) and user risk profile.
    
    Args:
        entry_price (float): The current price of the asset (assumed entry).
        atr_value (float): The current Average True Range of the asset.
        risk_tolerance (str): User risk profile ('Conservative', 'Moderate', 'Aggressive').
        
    Returns:
        Dict[str, Any]: A dictionary containing stop_loss, take_profit, and the calculated R:R ratio.
    """
    
    # Normalize risk tolerance
    rt = risk_tolerance.strip().title()
    if rt not in ["Conservative", "Moderate", "Aggressive"]:
        rt = "Moderate" # Default
        
    # Define multiplier rules based on risk tolerance
    # Target R:R for Conservative is ~ 3:1
    # Target R:R for Moderate is ~ 2:1
    # Target R:R for Aggressive is ~ 1.5:1
    
    if rt == "Conservative":
        stop_loss_multiplier = 1.0
        take_profit_multiplier = 3.0
    elif rt == "Aggressive":
        stop_loss_multiplier = 2.0
        take_profit_multiplier = 3.0 # R:R = 1.5
    else: # Moderate
        stop_loss_multiplier = 1.5
        take_profit_multiplier = 3.0 # R:R = 2.0
        
    stop_loss_dist = atr_value * stop_loss_multiplier
    take_profit_dist = atr_value * take_profit_multiplier
    
    stop_loss_price = round(entry_price - stop_loss_dist, 2)
    take_profit_price = round(entry_price + take_profit_dist, 2)
    
    actual_rr = round(take_profit_dist / stop_loss_dist, 2)
    
    return {
        "entry_price": round(entry_price, 2),
        "atr_value": round(atr_value, 2),
        "risk_tolerance": rt,
        "stop_loss_price": stop_loss_price,
        "take_profit_price": take_profit_price,
        "risk_reward_ratio": f"{actual_rr}:1",
        "actionable_signal": f"Stop-Loss at ${stop_loss_price}. Target at ${take_profit_price}. R:R is {actual_rr}:1."
    }

if __name__ == "__main__":
    # Test
    res = calculate_risk_reward(135.0, 5.5, "Moderate")
    print(res)
