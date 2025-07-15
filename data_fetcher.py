# data_fetcher.py

import yfinance as yf
import pandas as pd
import datetime
import os
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.techindicators import TechIndicators
import time

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

def get_usd_inr_rate_alphavantage():
    """
    Fetches the current USD to INR exchange rate using Alpha Vantage API.
    Requires ALPHA_VANTAGE_API_KEY environment variable.
    """
    try:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY environment variable not set")
        
        fx = ForeignExchange(key=api_key, output_format='pandas')
        data, meta_data = fx.get_currency_exchange_rate(from_currency='USD', to_currency='INR')
        
        if not data.empty:
            # Extract the exchange rate
            return float(data['5. Exchange Rate'].iloc[0])
        else:
            raise ValueError("No current exchange rate data found from Alpha Vantage")
    
    except Exception as e:
        raise Exception(f"Failed to fetch current USD/INR rate from Alpha Vantage: {e}")

def get_alphavantage_intraday_data(interval='5min', outputsize='compact'):
    """
    Fetches intraday USD/INR data from Alpha Vantage.
    
    Args:
        interval (str): Time interval ('1min', '5min', '15min', '30min', '60min')
        outputsize (str): 'compact' (last 100 data points) or 'full' (full historical data)
    
    Returns:
        pd.DataFrame: DataFrame with OHLC data and datetime index
    """
    try:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY environment variable not set")
        
        fx = ForeignExchange(key=api_key, output_format='pandas')
        
        # Get intraday data
        data, meta_data = fx.get_fx_intraday(
            from_symbol='USD',
            to_symbol='INR',
            interval=interval,
            outputsize=outputsize
        )
        
        if not data.empty:
            # Rename columns to match expected format
            data.columns = ['Open', 'High', 'Low', 'Close']
            
            # Convert index to datetime if not already
            data.index = pd.to_datetime(data.index)
            
            # Sort by datetime (ascending)
            data = data.sort_index()
            
            # Convert to float
            data = data.astype(float)
            
            return data
        else:
            raise ValueError("No intraday data found from Alpha Vantage")
    
    except Exception as e:
        raise Exception(f"Failed to fetch intraday data from Alpha Vantage: {e}")

def get_alphavantage_daily_data(outputsize='compact'):
    """
    Fetches daily USD/INR data from Alpha Vantage.
    
    Args:
        outputsize (str): 'compact' (last 100 data points) or 'full' (full historical data)
    
    Returns:
        pd.DataFrame: DataFrame with OHLC data and datetime index
    """
    try:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY environment variable not set")
        
        fx = ForeignExchange(key=api_key, output_format='pandas')
        
        # Get daily data
        data, meta_data = fx.get_fx_daily(
            from_symbol='USD',
            to_symbol='INR',
            outputsize=outputsize
        )
        
        if not data.empty:
            # Rename columns to match expected format
            data.columns = ['Open', 'High', 'Low', 'Close']
            
            # Convert index to datetime if not already
            data.index = pd.to_datetime(data.index)
            
            # Sort by datetime (ascending)
            data = data.sort_index()
            
            # Convert to float
            data = data.astype(float)
            
            return data
        else:
            raise ValueError("No daily data found from Alpha Vantage")
    
    except Exception as e:
        raise Exception(f"Failed to fetch daily data from Alpha Vantage: {e}")

def get_live_candlestick_data(timeframe='5min', data_source='alphavantage'):
    """
    Unified function to get live candlestick data from different sources.
    
    Args:
        timeframe (str): '1min', '5min', '15min', '30min', '60min', '1d'
        data_source (str): 'alphavantage' or 'yfinance'
    
    Returns:
        pd.DataFrame: DataFrame with OHLC data and datetime index
    """
    try:
        if data_source == 'alphavantage':
            if timeframe == '1d':
                return get_alphavantage_daily_data()
            else:
                return get_alphavantage_intraday_data(interval=timeframe)
        
        elif data_source == 'yfinance':
            # For yfinance, we can only get daily data for USD/INR
            if timeframe in ['1min', '5min', '15min', '30min', '60min']:
                # Try to get intraday data, but it's unlikely to work for USD/INR
                try:
                    return get_yfinance_candlestick_data(
                        symbol="USDINR=X", 
                        period="1d", 
                        interval=timeframe
                    )
                except:
                    # Fall back to daily data
                    return get_yfinance_candlestick_data(
                        symbol="USDINR=X", 
                        period="1mo", 
                        interval="1d"
                    )
            else:
                period_map = {
                    '1d': '1mo',
                    '1w': '6mo',
                    '1M': '1y'
                }
                period = period_map.get(timeframe, '1mo')
                return get_yfinance_candlestick_data(
                    symbol="USDINR=X", 
                    period=period, 
                    interval="1d"
                )
        
        else:
            raise ValueError(f"Unsupported data source: {data_source}")
    
    except Exception as e:
        # Try fallback to yfinance if Alpha Vantage fails
        if data_source == 'alphavantage':
            try:
                return get_live_candlestick_data(timeframe='1d', data_source='yfinance')
            except:
                raise Exception(f"Both Alpha Vantage and yfinance failed: {e}")
        else:
            raise Exception(f"Failed to fetch live candlestick data: {e}")

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

def get_current_rate_with_fallback():
    """
    Gets current USD/INR rate with fallback mechanism.
    Tries Alpha Vantage first, then falls back to yfinance.
    """
    try:
        # Try Alpha Vantage first
        return get_usd_inr_rate_alphavantage()
    except Exception as e:
        print(f"Alpha Vantage failed: {e}")
        try:
            # Fall back to yfinance
            return get_usd_inr_rate()
        except Exception as e2:
            raise Exception(f"Both Alpha Vantage and yfinance failed. Alpha Vantage: {e}, yfinance: {e2}")

# Example of how to test this function (optional, for local debugging)
if __name__ == "__main__":
    try:
        # Test current rate
        current_rate = get_current_rate_with_fallback()
        print(f"Current USD/INR rate: ₹{current_rate:.2f}")

        # Test Alpha Vantage intraday data
        print("\nTesting Alpha Vantage 5min intraday data:")
        intraday_data = get_live_candlestick_data(timeframe='5min', data_source='alphavantage')
        print(intraday_data.tail())

        # Test yfinance daily data
        print("\nTesting yfinance daily data:")
        daily_data = get_yfinance_candlestick_data(period='7d', interval='1d')
        print(daily_data.tail())

    except Exception as e:
        print(f"Error: {e}")
