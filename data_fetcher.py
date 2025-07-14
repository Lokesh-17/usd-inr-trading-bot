# data_fetcher.py

from binance.client import Client
import pandas as pd
import datetime

# Initialize Binance client (no API key needed for public endpoints)
# If you ever need authenticated endpoints, you would set BINANCE_API_KEY and BINANCE_API_SECRET as env vars
client = Client("", "") # Empty API key and secret for public access

def get_usd_inr_rate():
    """
    Fetches the current USDT/INR exchange rate from Binance Spot API.
    USDT (Tether) is a stablecoin pegged to the US Dollar, serving as a proxy for USD.
    """
    symbol = "USDTINR"
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        if ticker and "price" in ticker:
            return float(ticker["price"])
        else:
            raise ValueError(f"Price data not found for {symbol} in Binance API response.")
    except Exception as e:
        raise Exception(f"Failed to fetch current USDT/INR rate from Binance: {e}")

def get_candlestick_data(symbol="USDTINR", interval=Client.KLINE_INTERVAL_1HOUR, limit=500):
    """
    Fetches historical candlestick data (OHLCV) for a given symbol and interval from Binance.
    Args:
        symbol (str): Trading pair symbol (e.g., "USDTINR").
        interval (str): Kline interval (e.g., Client.KLINE_INTERVAL_1MINUTE, Client.KLINE_INTERVAL_1HOUR).
        limit (int): Number of most recent candles to fetch.
    Returns:
        pd.DataFrame: DataFrame with 'Open', 'High', 'Low', 'Close', 'Volume', 'Datetime' columns.
    """
    try:
        klines = client.get_historical_klines(symbol, interval, limit=limit)

        # Process klines data into a pandas DataFrame
        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])

        # Convert timestamp to datetime and set as index
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        df = df.rename(columns={'open_time': 'Datetime'})
        df = df.set_index('Datetime')

        # Convert OHLCV columns to numeric
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col])

        # Select relevant columns for the chart
        return df[['open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        raise Exception(f"Failed to fetch candlestick data from Binance: {e}")

# Example of how to test this function (optional, for local debugging)
if __name__ == "__main__":
    try:
        current_rate = get_usd_inr_rate()
        print(f"Current USDT/INR rate: ₹{current_rate:.2f}")

        candlesticks = get_candlestick_data(interval=Client.KLINE_INTERVAL_1MINUTE, limit=10)
        print("\nLast 10 Minute Candlesticks:")
        print(candlesticks)
    except Exception as e:
        print(f"Error: {e}")

