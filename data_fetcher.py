# data_fetcher.py

import requests
import os

def get_usd_inr_rate():
    """
    Fetches the current USD to INR exchange rate from ExchangeRate-API.
    Requires an API key set as an environment variable named EXCHANGE_RATE_API_KEY.
    """
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        raise ValueError("EXCHANGE_RATE_API_KEY environment variable not set.")

    base_currency = "USD"
    target_currency = "INR"
    api_url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base_currency}/{target_currency}"

    try:
        response = requests.get(api_url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data.get("result") == "success" and "conversion_rate" in data:
            return float(data["conversion_rate"])
        elif data.get("result") == "error":
            error_type = data.get("error-type", "unknown_error")
            raise ValueError(f"ExchangeRate-API error: {error_type}. Response: {data}")
        else:
            raise ValueError(f"Unexpected response from ExchangeRate-API: {data}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Could not connect to ExchangeRate-API: {e}")
    except ValueError as e:
        raise ValueError(f"Error parsing ExchangeRate-API response: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while fetching data: {e}")

# Example of how to test this function (optional, for local debugging)
if __name__ == "__main__":
    # For local testing, set the environment variable temporarily:
    # export EXCHANGE_RATE_API_KEY="YOUR_ACTUAL_EXCHANGE_RATE_API_KEY"
    try:
        rate = get_usd_inr_rate()
        print(f"Current USD/INR rate from ExchangeRate-API: ₹{rate:.2f}")
    except (ConnectionError, ValueError, Exception) as e:
        print(f"Failed to fetch rate: {e}")

