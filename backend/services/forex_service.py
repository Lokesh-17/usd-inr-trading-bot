import requests
import pandas as pd
import os
from typing import Dict, List
from datetime import datetime
import asyncio
import aiohttp

class ForexService:
    def __init__(self):
        self.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
        
        if not self.alpha_vantage_api_key:
            print("WARNING: ALPHA_VANTAGE_API_KEY environment variable is not set.")
    
    async def get_usd_inr_rate(self) -> float:
        """Get current USD to INR exchange rate"""
        if not self.alpha_vantage_api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY is not set.")
        
        params = {
            "function": "FX_DAILY",
            "from_symbol": "USD",
            "to_symbol": "INR",
            "apikey": self.alpha_vantage_api_key
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    if "Time Series FX (Daily)" in data:
                        # Get the most recent day's data
                        latest_day = list(data["Time Series FX (Daily)"].keys())[0]
                        current_rate = float(data["Time Series FX (Daily)"][latest_day]["4. close"])
                        return current_rate
                    elif "Error Message" in data:
                        raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")
                    else:
                        raise ValueError(f"Unexpected response from Alpha Vantage API: {data}")
                        
            except aiohttp.ClientError as e:
                raise ConnectionError(f"Could not connect to Alpha Vantage API: {e}")
            except Exception as e:
                raise Exception(f"An unexpected error occurred while fetching exchange rate: {e}")
    
    async def get_candlestick_data(self, interval: str = "5min", outputsize: str = "compact") -> Dict:
        """Get candlestick chart data for USD/INR"""
        if not self.alpha_vantage_api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY is not set.")
        
        params = {
            "function": "FX_INTRADAY",
            "from_symbol": "USD",
            "to_symbol": "INR",
            "interval": interval,
            "outputsize": outputsize,
            "apikey": self.alpha_vantage_api_key
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    time_series_key = f"Time Series FX ({interval})"
                    if time_series_key in data:
                        raw_data = data[time_series_key]
                        
                        # Convert to list of candlestick objects
                        candlesticks = []
                        for timestamp, ohlcv in raw_data.items():
                            candlesticks.append({
                                "timestamp": timestamp,
                                "open": float(ohlcv["1. open"]),
                                "high": float(ohlcv["2. high"]),
                                "low": float(ohlcv["3. low"]),
                                "close": float(ohlcv["4. close"]),
                                "volume": float(ohlcv["5. volume"])
                            })
                        
                        # Sort by timestamp (most recent first)
                        candlesticks.sort(key=lambda x: x["timestamp"], reverse=True)
                        
                        return {
                            "data": candlesticks,
                            "interval": interval,
                            "symbol": "USD/INR"
                        }
                    elif "Error Message" in data:
                        raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")
                    elif "Note" in data:
                        raise ConnectionError(f"Alpha Vantage API Note: {data['Note']}. Likely rate limit hit.")
                    else:
                        raise ValueError(f"Unexpected response from Alpha Vantage API: {data}")
                        
            except aiohttp.ClientError as e:
                raise ConnectionError(f"Could not connect to Alpha Vantage API: {e}")
            except Exception as e:
                raise Exception(f"An unexpected error occurred while fetching chart data: {e}")
    
    def calculate_sma(self, data: List[Dict], period: int, price_key: str = "close") -> List[float]:
        """Calculate Simple Moving Average"""
        sma_values = []
        for i in range(len(data)):
            if i < period - 1:
                sma_values.append(None)
            else:
                window_data = data[i-period+1:i+1]
                sma = sum(candle[price_key] for candle in window_data) / period
                sma_values.append(sma)
        return sma_values
    
    def generate_trading_signals(self, data: List[Dict], short_sma_period: int = 20, long_sma_period: int = 50) -> List[Dict]:
        """Generate trading signals based on SMA crossover"""
        if len(data) < long_sma_period:
            return data
        
        # Calculate SMAs
        short_sma = self.calculate_sma(data, short_sma_period)
        long_sma = self.calculate_sma(data, long_sma_period)
        
        # Add SMA values and signals to data
        for i, candle in enumerate(data):
            candle["sma_short"] = short_sma[i]
            candle["sma_long"] = long_sma[i]
            
            # Generate signal
            if i > 0 and short_sma[i] is not None and long_sma[i] is not None:
                prev_short = short_sma[i-1]
                prev_long = long_sma[i-1]
                
                if (prev_short is not None and prev_long is not None and
                    prev_short <= prev_long and short_sma[i] > long_sma[i]):
                    candle["signal"] = "BUY"
                elif (prev_short is not None and prev_long is not None and
                      prev_short >= prev_long and short_sma[i] < long_sma[i]):
                    candle["signal"] = "SELL"
                else:
                    candle["signal"] = "HOLD"
            else:
                candle["signal"] = "HOLD"
        
        return data