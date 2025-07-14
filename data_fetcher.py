# data_fetcher.py

import yfinance as yf
from pycoingecko import CoinGeckoAPI
import pandas as pd
import datetime

# Initialize CoinGecko API client
cg = CoinGeckoAPI()

def get_usd_inr_rate():
    """
    Fetches the current USD to INR exchange rate using yfinance.
    Note: yfinance primarily provides market data, and direct forex pairs
    might be less real-time or accurate compared to dedicated forex APIs.
    However, it's suitable for general trends.
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
        raise Exception(f"Failed to fetch USD/INR rate from yfinance: {e}")

def get_coingecko_candlestick_data(coin_id='bitcoin', vs_currency='inr', days='30'):
    """
    Fetches historical candlestick data (OHLCV) for a given cryptocurrency from CoinGecko.
    Args:
        coin_id (str): The CoinGecko ID of the coin (e.g., 'bitcoin', 'ethereum').
        vs_currency (str): The target currency (e.g., 'usd', 'inr').
        days (str): Number of days of data to fetch (e.g., '1', '7', '30', 'max').
    Returns:
        pd.DataFrame: DataFrame with 'Open', 'High', 'Low', 'Close', 'Datetime' columns.
    """
    try:
        # CoinGecko API for market chart data (includes OHLC)
        # The 'ohlc' endpoint provides OHLC data directly
        ohlc_data = cg.get_coin_ohlc_by_id(id=coin_id, vs_currency=vs_currency, days=days)

        if not ohlc_data:
            raise ValueError(f"No OHLC data found for {coin_id}/{vs_currency} from CoinGecko for {days} days.")

        # Convert to DataFrame
        df = pd.DataFrame(ohlc_data, columns=['timestamp', 'open', 'high', 'low', 'close'])

        # Convert timestamp to datetime and set as index
        df['Datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('Datetime')

        # Convert OHLC columns to numeric
        numeric_cols = ['open', 'high', 'low', 'close']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col])

        return df[['open', 'high', 'low', 'close']] # Volume is not directly available from this endpoint
    except Exception as e:
        raise Exception(f"Failed to fetch historical data from CoinGecko: {e}")

# Example of how to test this function (optional, for local debugging)
if __name__ == "__main__":
    try:
        current_rate = get_usd_inr_rate()
        print(f"Current USD/INR rate (YFinance): ₹{current_rate:.2f}")

        candlesticks = get_coingecko_candlestick_data(coin_id='bitcoin', vs_currency='inr', days='7')
        print("\nLast 7 Days BTC/INR Candlesticks (CoinGecko):")
        print(candlesticks.head())
    except Exception as e:
        print(f"Error: {e}")
