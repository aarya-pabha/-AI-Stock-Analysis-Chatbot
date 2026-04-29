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

def get_growth_metrics(ticker: str, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Fetches YoY Revenue and EPS growth rates. Supports end_date for point-in-time accuracy."""
    try:
        tkr = yf.Ticker(ticker)
        
        if not end_date:
            info = tkr.info
            return {
                "revenueGrowth": info.get("revenueGrowth", None),
                "earningsGrowth": info.get("earningsGrowth", None),
                "trailingPE": info.get("trailingPE", None),
                "forwardPE": info.get("forwardPE", None)
            }
        
        # Historical mode: Calculate from financial statements
        financials = tkr.financials.T
        if financials.empty:
            return {"error": "No historical financials found."}
        
        financials.index = pd.to_datetime(financials.index)
        hist_fin = financials[financials.index <= end_date]
        if hist_fin.empty:
            return {"warning": "Historical point-in-time fundamental data is unavailable for this date. This is a data limitation, NOT a sign of poor financial health. Do not penalize the asset."}
            
        latest_rev = hist_fin["Total Revenue"].iloc[0] if "Total Revenue" in hist_fin else None
        prev_rev = hist_fin["Total Revenue"].iloc[1] if len(hist_fin) > 1 and "Total Revenue" in hist_fin else None
        
        if latest_rev is None or prev_rev is None or pd.isna(latest_rev) or pd.isna(prev_rev):
             return {"warning": "Insufficient historical revenue data to calculate growth. This is a data limitation, NOT a sign of poor financial health."}
        
        rev_growth = (latest_rev - prev_rev) / prev_rev
        
        return {
            "revenueGrowth": round(float(rev_growth), 4),
            "simulated_point_in_time": True,
            "note": "Growth calculated from last two annual statements relative to simulated date."
        }
    except Exception as e:
        return {"error": f"Failed to fetch growth metrics: {str(e)}"}

def get_risk_metrics(ticker: str, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Fetches Debt-to-Equity and margins. Supports end_date."""
    try:
        tkr = yf.Ticker(ticker)
        if not end_date:
            info = tkr.info
            return {
                "debtToEquity": info.get("debtToEquity", None),
                "profitMargins": info.get("profitMargins", None),
                "operatingMargins": info.get("operatingMargins", None)
            }
            
        bs = tkr.balance_sheet.T
        if bs.empty:
            return {"error": "No historical balance sheet found."}
        bs.index = pd.to_datetime(bs.index)
        hist_bs = bs[bs.index <= end_date]
        
        if hist_bs.empty:
            return {"warning": "Historical balance sheet data is unavailable for this date. This is a data limitation, NOT a sign of poor financial health. Do not penalize the asset."}
            
        latest_bs = hist_bs.iloc[0]
        total_debt = latest_bs.get("Total Debt", 0)
        equity = latest_bs.get("Stockholders Equity", 1)
        
        return {
            "debtToEquity": round(float(total_debt / equity), 4) if equity else None,
            "simulated_point_in_time": True
        }
    except Exception as e:
        return {"error": f"Failed to fetch risk metrics: {str(e)}"}

def get_insider_activity(ticker: str, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Fetches recent open-market purchases/dumps. Supports end_date."""
    try:
        tkr = yf.Ticker(ticker)
        insider = tkr.insider_transactions
        if insider is None or insider.empty:
            return {"insider_activity": "No recent data available."}
        
        if end_date:
            # yfinance insider table date column name varies, usually 'Start Date'
            date_col = 'Start Date' if 'Start Date' in insider.columns else 'Date'
            insider[date_col] = pd.to_datetime(insider[date_col])
            insider = insider[insider[date_col] <= end_date]
        
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

def get_short_interest_data(ticker: str, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Checks percentage of float shorted. Supports end_date (simulated)."""
    try:
        if end_date:
            return {"warning": "Historical short interest data unavailable for simulated date. Skipping."}
            
        tkr = yf.Ticker(ticker)
        info = tkr.info
        return {
            "shortPercentOfFloat": info.get("shortPercentOfFloat", None),
            "shortRatio": info.get("shortRatio", None) 
        }
    except Exception as e:
        return {"error": f"Failed to fetch short interest data: {str(e)}"}

def get_analyst_upgrades(ticker: str, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Fetches Wall Street price target changes. Supports end_date."""
    try:
        tkr = yf.Ticker(ticker)
        recs = tkr.upgrades_downgrades
        if recs is None or recs.empty:
            return {"analyst_recs": "No recent upgrades/downgrades found."}
        
        if end_date:
            recs.index = pd.to_datetime(recs.index)
            recs = recs[recs.index <= end_date]
            
        recent = recs.head(5)
        summary = []
        for index, row in recent.iterrows():
            date_str = str(index.date()) if hasattr(index, 'date') else str(index)
            summary.append(f"{date_str}: {row.get('Firm', '')} {row.get('Action', '')} to {row.get('ToGrade', '')}")
            
        return {
            "recent_actions": summary,
            "note": f"Analyst actions relative to {end_date if end_date else 'present'}."
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
