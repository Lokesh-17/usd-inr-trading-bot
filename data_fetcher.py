# data_fetcher.py

import yfinance as yf
import pandas as pd
import datetime

def get_usd_inr_rate():
    """
    Fetches the current USD to INR exchange rate using yfinance.
    """
    try:
        # USDINR=X is the Yahoo Finance symbol for USD/INR
        ticker = yf.Ticker("USDINR=X")
        # Get the most recent data point
        data = ticker.history(period="1d")

        if not data.empty:
            # The 'Close' price for the most recent day
            return data['Close'].iloc[-1]
        else:
            raise ValueError("No data found for USDINR=X. Check the ticker symbol or market availability.")

    except Exception as e:
        raise Exception(f"Failed to fetch current USD/INR rate from yfinance: {e}")

def get_yfinance_candlestick_data(symbol="USDINR=X", period="1mo", interval="1d"):
    """
    Fetches historical candlestick data (OHLC) for a given symbol from yfinance.
    Note: For forex pairs like USDINR=X, yfinance typically provides daily intervals.
    Intraday intervals (like 1m, 5m, 1h) are usually not available for forex on yfinance.
    Args:
        symbol (str): Trading pair symbol (e.g., "USDINR=X").
        period (str): Data period (e.g., "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max").
        interval (str): Data interval (e.g., "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo").
                      For USDINR=X, "1d" is usually the most granular available.
    Returns:
        pd.DataFrame: DataFrame with 'Open', 'High', 'Low', 'Close' columns and Datetime index.
    """
    try:
        ticker = yf.Ticker(symbol)
        hist_data = ticker.history(period=period, interval=interval)

        if not hist_data.empty:
            # Reset index to make 'Date' a column for Plotly, then set it back as index
            hist_data = hist_data.reset_index()
            hist_data['Datetime'] = pd.to_datetime(hist_data['Date']) # Ensure Datetime is datetime
            hist_data = hist_data.set_index('Datetime')
            # Select only OHLC for the chart
            return hist_data[['Open', 'High', 'Low', 'Close']]
        else:
            raise ValueError(f"No historical data found for {symbol} for period {period} and interval {interval}.")

    except Exception as e:
        raise Exception(f"Failed to fetch historical data from yfinance: {e}")

# Example of how to test this function (optional, for local debugging)
if __name__ == "__main__":
    try:
        current_rate = get_usd_inr_rate()
        print(f"Current USD/INR rate (YFinance): ₹{current_rate:.2f}")

        candlesticks = get_yfinance_candlestick_data(period='7d', interval='1d')
        print("\nLast 7 Days USD/INR Candlesticks (YFinance):")
        print(candlesticks.head())
    except Exception as e:
        print(f"Error: {e}")
