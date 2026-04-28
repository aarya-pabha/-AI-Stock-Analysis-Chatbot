import yfinance as yf
import mplfinance as mpf
import pandas as pd
from pathlib import Path
from typing import Optional

def generate_multimodal_chart(ticker: str, timeframe: str = "daily", save_dir: str = "data") -> Optional[str]:
    """
    Fetches OHLCV data for a ticker and generates a high-resolution .png candlestick chart 
    with volume and moving averages plotted for VLM analysis.
    
    Args:
        ticker (str): The stock symbol (e.g., 'AAPL').
        timeframe (str): 'daily' or 'weekly'.
        save_dir (str): The directory to save the generated image.
        
    Returns:
        Optional[str]: The absolute path to the saved .png file, or None if failed.
    """
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    
    # Configure period and interval based on timeframe
    if timeframe.lower() == "weekly":
        period = "2y"
        interval = "1wk"
        file_suffix = "weekly"
    else:
        period = "6mo"
        interval = "1d"
        file_suffix = "daily"

    try:
        # Fetch data
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        
        if df.empty:
            print(f"Error: No data found for {ticker}.")
            return None
            
        # Clean up column names for mplfinance (yfinance returns multi-index sometimes)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            
        # Ensure required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
            print(f"Error: Missing required OHLCV columns for {ticker}.")
            return None

        # Setup plot style and parameters
        mc = mpf.make_marketcolors(up='g', down='r', edge='i', wick='i', volume='in', ohlc='i')
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', y_on_right=False)
        
        # Output file path
        output_file = save_path / f"{ticker.upper()}_{file_suffix}_chart.png"
        
        # Plot and save
        mpf.plot(
            df,
            type='candle',
            volume=True,
            mav=(20, 50),  # Plot 20-period and 50-period moving averages
            style=s,
            title=f"{ticker.upper()} {timeframe.capitalize()} Chart",
            ylabel='Price ($)',
            ylabel_lower='Volume',
            savefig=dict(fname=str(output_file), dpi=300, bbox_inches='tight')
        )
        
        return str(output_file.absolute())
        
    except Exception as e:
        print(f"Failed to generate chart for {ticker}: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the function
    res = generate_multimodal_chart("NVDA", "daily")
    if res:
        print(f"Successfully saved chart to: {res}")
