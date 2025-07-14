# data_fetcher.py

import yfinance as yf

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

# Example of how to test this function (optional, for local debugging)
if __name__ == "__main__":
    try:
        rate = get_usd_inr_rate()
        print(f"Current USD/INR rate from YFinance: ₹{rate:.2f}")
    except Exception as e:
        print(f"Failed to fetch rate: {e}")

