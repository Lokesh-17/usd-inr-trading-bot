# data_fetcher.py

import requests
import pandas as pd
import datetime
import os

# --- Alpha Vantage API Configuration ---
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Check if API key is set
if not ALPHA_VANTAGE_API_KEY:
    print("WARNING: ALPHA_VANTAGE_API_KEY environment variable is not set. Data fetching will fail.")


def get_usd_inr_rate():
    """
    Fetches the current USD to INR exchange rate from Alpha Vantage.
    Uses FX_DAILY for a recent close price, as real-time tick data is paid.
    """
    if not ALPHA_VANTAGE_API_KEY:
        raise ValueError("ALPHA_VANTAGE_API_KEY is not set.")

    params = {
        "function": "FX_DAILY",
        "from_symbol": "USD",
        "to_symbol": "INR",
        "apikey": ALPHA_VANTAGE_API_KEY
    }

    try:
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if "Time Series FX (Daily)" in data:
            # Get the most recent day's data
            latest_day = list(data["Time Series FX (Daily)"].keys())[0]
            current_rate = float(data["Time Series FX (Daily)"][latest_day]["4. close"])
            return current_rate
        elif "Error Message" in data:
            raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")
        else:
            raise ValueError(f"Unexpected response from Alpha Vantage API for current rate: {data}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Could not connect to Alpha Vantage API for current price: {e}")
    except ValueError as e:
        raise ValueError(f"Error parsing Alpha Vantage API response for current price: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while fetching current price: {e}")


def get_alpha_vantage_candlestick_data(symbol="USD", to_symbol="INR", interval="60min", outputsize="compact"):
    """
    Fetches intraday candlestick data (OHLCV) for a given forex pair from Alpha Vantage.
    Free tier limits apply: 5 requests/minute, 500 requests/day.
    Args:
        symbol (str): Base currency (e.g., "USD").
        to_symbol (str): Target currency (e.g., "INR").
        interval (str): Time interval (e.g., "1min", "5min", "15min", "30min", "60min").
        outputsize (str): "compact" (last 100 points) or "full" (all available data).
    Returns:
        pd.DataFrame: DataFrame with 'Open', 'High', 'Low', 'Close', 'Volume' columns and Datetime index.
    """
    if not ALPHA_VANTAGE_API_KEY:
        raise ValueError("ALPHA_VANTAGE_API_KEY is not set.")

    params = {
        "function": "FX_INTRADAY",
        "from_symbol": symbol,
        "to_symbol": to_symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": ALPHA_VANTAGE_API_KEY
    }

    try:
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        time_series_key = f"Time Series FX ({interval})"
        if time_series_key in data:
            raw_data = data[time_series_key]
            df = pd.DataFrame.from_dict(raw_data, orient='index', dtype=float)
            df.index = pd.to_datetime(df.index)
            df = df.sort_index() # Ensure chronological order

            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df.index.name = 'Datetime'
            return df[['Open', 'High', 'Low', 'Close', 'Volume']]
        elif "Error Message" in data:
            raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")
        elif "Note" in data:
            # This often means rate limit hit
            raise ConnectionError(f"Alpha Vantage API Note: {data['Note']}. Likely rate limit hit.")
        else:
            raise ValueError(f"Unexpected response from Alpha Vantage API for klines: {data}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Could not connect to Alpha Vantage API for klines: {e}")
    except ValueError as e:
        raise ValueError(f"Error parsing Alpha Vantage API response for klines: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while fetching klines: {e}")

# Example of how to test this function (optional, for local debugging)
if __name__ == "__main__":
    # For local testing, set the environment variable temporarily:
    # export ALPHA_VANTAGE_API_KEY="YOUR_ACTUAL_ALPHA_VANTAGE_API_KEY"
    try:
        current_rate = get_usd_inr_rate()
        print(f"Current USD/INR rate (Alpha Vantage): ₹{current_rate:.2f}")

        # Test with a 5-minute interval for the last 100 data points
        candlesticks = get_alpha_vantage_candlestick_data(interval="5min", outputsize="compact")
        print("\nLast 100 5-Minute USD/INR Candlesticks (Alpha Vantage):")
        print(candlesticks.head())
    except Exception as e:
        print(f"Error: {e}")

