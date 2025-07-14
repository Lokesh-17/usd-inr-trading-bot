# data_fetcher.py
import yfinance as yf

def get_usd_inr_rate():
    ticker = yf.Ticker("USDINR=X")
    data = ticker.history(period="1d")
    if not data.empty:
        latest_rate = round(data["Close"].iloc[-1], 2)
        return latest_rate
    else:
        return "Exchange rate not available"
