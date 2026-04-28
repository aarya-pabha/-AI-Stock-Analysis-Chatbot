import os
import yfinance as yf
import pandas as pd
from openbb import obb
from typing import Dict, Any, Optional

# Authenticate OpenBB if Personal Access Token is available
openbb_pat = os.getenv("OPENBB_PAT")
if openbb_pat:
    try:
        obb.account.login(pat=openbb_pat)
        print("Successfully authenticated OpenBB.")
    except Exception as e:
        print(f"Warning: Failed to authenticate OpenBB: {e}")

def get_momentum_indicators(ticker: str, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Returns JSON of RSI, MACD, and Stochastic oscillators. Supports end_date for backtesting."""
    try:
        # Fetch historical data using yfinance provider
        if end_date:
            stock_data = obb.equity.price.historical(symbol=ticker, provider="yfinance", end_date=end_date)
        else:
            stock_data = obb.equity.price.historical(symbol=ticker, provider="yfinance")
        df = stock_data.to_df()
        
        # Calculate RSI
        rsi = obb.technical.rsi(data=df, target="close", length=14).to_df()
        # Calculate MACD
        macd = obb.technical.macd(data=df, target="close", fast=12, slow=26, signal=9).to_df()
        
        # Safely extract latest values
        rsi_val = rsi.iloc[-1].get("close_RSI_14", None)
        macd_val = macd.iloc[-1].get("close_MACD_12_26_9", None)
        macd_hist = macd.iloc[-1].get("close_MACDh_12_26_9", None)

        return {
            "rsi_14": round(float(rsi_val), 2) if pd.notnull(rsi_val) else None,
            "macd": round(float(macd_val), 2) if pd.notnull(macd_val) else None,
            "macd_histogram": round(float(macd_hist), 2) if pd.notnull(macd_hist) else None,
            "momentum_signal": "Bullish" if pd.notnull(macd_hist) and macd_hist > 0 else "Bearish"
        }
    except Exception as e:
        return {"error": f"Failed to calculate momentum indicators: {str(e)}"}

def get_volatility_indicators(ticker: str, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Returns JSON of Bollinger Bands and Average True Range (ATR). Supports end_date."""
    try:
        if end_date:
            stock_data = obb.equity.price.historical(symbol=ticker, provider="yfinance", end_date=end_date)
        else:
            stock_data = obb.equity.price.historical(symbol=ticker, provider="yfinance")
        df = stock_data.to_df()
        
        bbands = obb.technical.bbands(data=df, target="close", length=20, std=2).to_df()
        atr = obb.technical.atr(data=df, length=14).to_df()
        
        # Safely extract latest values
        bb_upper = bbands.iloc[-1].get("close_BBU_20_2.0", None)
        bb_lower = bbands.iloc[-1].get("close_BBL_20_2.0", None)
        bb_mid = bbands.iloc[-1].get("close_BBM_20_2.0", None)
        atr_val = atr.iloc[-1].get("ATRr_14", None)

        return {
            "atr_14": round(float(atr_val), 2) if pd.notnull(atr_val) else None,
            "bbands_upper": round(float(bb_upper), 2) if pd.notnull(bb_upper) else None,
            "bbands_middle": round(float(bb_mid), 2) if pd.notnull(bb_mid) else None,
            "bbands_lower": round(float(bb_lower), 2) if pd.notnull(bb_lower) else None
        }
    except Exception as e:
        return {"error": f"Failed to calculate volatility indicators: {str(e)}"}

def get_growth_metrics(ticker: str) -> Dict[str, Any]:
    """Fetches YoY Revenue and EPS growth rates."""
    try:
        # Fallback to yfinance to ensure reliable access without premium OpenBB providers
        tkr = yf.Ticker(ticker)
        info = tkr.info
        return {
            "revenueGrowth": info.get("revenueGrowth", None),
            "earningsGrowth": info.get("earningsGrowth", None),
            "trailingPE": info.get("trailingPE", None),
            "forwardPE": info.get("forwardPE", None)
        }
    except Exception as e:
        return {"error": f"Failed to fetch growth metrics: {str(e)}"}

def get_risk_metrics(ticker: str) -> Dict[str, Any]:
    """Fetches Debt-to-Equity ratio and declining profit margins."""
    try:
        tkr = yf.Ticker(ticker)
        info = tkr.info
        return {
            "debtToEquity": info.get("debtToEquity", None),
            "profitMargins": info.get("profitMargins", None),
            "operatingMargins": info.get("operatingMargins", None)
        }
    except Exception as e:
        return {"error": f"Failed to fetch risk metrics: {str(e)}"}

def get_insider_activity(ticker: str) -> Dict[str, Any]:
    """Fetches recent open-market purchases/dumps by executives."""
    try:
        tkr = yf.Ticker(ticker)
        insider = tkr.insider_transactions
        if insider is None or insider.empty:
            return {"insider_activity": "No recent data available."}
        
        recent = insider.head(10)
        buy_shares = 0
        sell_shares = 0
        
        for _, row in recent.iterrows():
            shares = row.get("Shares", 0)
            if pd.notnull(shares):
                if shares > 0:
                    buy_shares += shares
                else:
                    sell_shares += abs(shares)
                    
        return {
            "recent_buy_shares": int(buy_shares),
            "recent_sell_shares": int(sell_shares),
            "net_activity": "Net Buying" if buy_shares > sell_shares else "Net Selling" if sell_shares > buy_shares else "Neutral"
        }
    except Exception as e:
        return {"error": f"Failed to fetch insider activity: {str(e)}"}

def get_short_interest_data(ticker: str) -> Dict[str, Any]:
    """Checks the percentage of float shorted and days-to-cover."""
    try:
        tkr = yf.Ticker(ticker)
        info = tkr.info
        return {
            "shortPercentOfFloat": info.get("shortPercentOfFloat", None),
            "shortRatio": info.get("shortRatio", None) # Days to cover
        }
    except Exception as e:
        return {"error": f"Failed to fetch short interest data: {str(e)}"}

def get_analyst_upgrades(ticker: str) -> Dict[str, Any]:
    """Fetches recent Wall Street price target increases/decreases."""
    try:
        tkr = yf.Ticker(ticker)
        recs = tkr.upgrades_downgrades
        if recs is None or recs.empty:
            return {"analyst_recs": "No recent upgrades/downgrades found."}
            
        recent = recs.head(5)
        summary = []
        for index, row in recent.iterrows():
            date_str = str(index.date()) if hasattr(index, 'date') else str(index)
            summary.append(f"{date_str}: {row.get('Firm', '')} {row.get('Action', '')} to {row.get('ToGrade', '')}")
            
        return {
            "targetMeanPrice": tkr.info.get("targetMeanPrice", None),
            "recommendationKey": tkr.info.get("recommendationKey", None),
            "recent_actions": summary
        }
    except Exception as e:
        return {"error": f"Failed to fetch analyst upgrades: {str(e)}"}

if __name__ == "__main__":
    # Test the tools
    ticker = "AAPL"
    print("Testing Momentum:", get_momentum_indicators(ticker))
    print("Testing Volatility:", get_volatility_indicators(ticker))
    print("Testing Growth:", get_growth_metrics(ticker))
    print("Testing Insider:", get_insider_activity(ticker))
