# data_fetcher.py

import requests
import pandas as pd
import datetime

# Constants for Binance API
BINANCE_API_BASE = "https://api.binance.com/api/v3"
SYMBOL = "USDTINR" # USDT to Indian Rupee

# Define intervals for klines (matching common use cases)
# These are the strings Binance API expects
KLINE_INTERVAL_1MINUTE = "1m"
KLINE_INTERVAL_5MINUTE = "5m"
KLINE_INTERVAL_15MINUTE = "15m"
KLINE_INTERVAL_30MINUTE = "30m"
KLINE_INTERVAL_1HOUR = "1h"
KLINE_INTERVAL_4HOUR = "4h"
KLINE_INTERVAL_1DAY = "1d"


def get_usd_inr_rate():
    """
    Fetches the current USDT/INR exchange rate from Binance Spot API using requests.
    USDT (Tether) is a stablecoin pegged to the US Dollar, serving as a proxy for USD.
    """
    endpoint = f"{BINANCE_API_BASE}/ticker/price"
    params = {"symbol": SYMBOL}

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if "price" in data:
            return float(data["price"])
        else:
            raise ValueError(f"Price data not found for {SYMBOL} in Binance API response: {data}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Could not connect to Binance API for current price: {e}")
    except ValueError as e:
        raise ValueError(f"Error parsing Binance API response for current price: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while fetching current price: {e}")


def get_candlestick_data(symbol=SYMBOL, interval=KLINE_INTERVAL_1HOUR, limit=500):
    """
    Fetches historical candlestick data (OHLCV) for a given symbol and interval from Binance using requests.
    Args:
        symbol (str): Trading pair symbol (e.g., "USDTINR").
        interval (str): Kline interval (e.g., "1m", "1h", "1d").
        limit (int): Number of most recent candles to fetch.
    Returns:
        pd.DataFrame: DataFrame with 'Open', 'High', 'Low', 'Close', 'Volume', 'Datetime' columns.
    """
    endpoint = f"{BINANCE_API_BASE}/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        klines = response.json()

        if not klines:
            raise ValueError(f"No kline data found for {symbol} with interval {interval}.")

        # Process klines data into a pandas DataFrame
        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])

        # Convert timestamp to datetime and set as index
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df = df.rename(columns={'open_time': 'Datetime'})
        df = df.set_index('Datetime')

        # Convert OHLCV columns to numeric
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col])

        # Select relevant columns for the chart
        return df[['open', 'high', 'low', 'close', 'volume']]
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Could not connect to Binance API for klines: {e}")
    except ValueError as e:
        raise ValueError(f"Error parsing Binance API response for klines: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while fetching klines: {e}")

# Example of how to test this function (optional, for local debugging)
if __name__ == "__main__":
    try:
        current_rate = get_usd_inr_rate()
        print(f"Current USDT/INR rate: ₹{current_rate:.2f}")

        candlesticks = get_candlestick_data(interval=KLINE_INTERVAL_1MINUTE, limit=5)
        print("\nLast 5 Minute Candlesticks:")
        print(candlesticks)
    except Exception as e:
        print(f"Error: {e}")

