import requests

def get_response_from_agent(user_input, exchange_api_key):
    if "price" in user_input.lower() or "usd to inr" in user_input.lower():
        url = f"https://v6.exchangerate-api.com/v6/{exchange_api_key}/pair/USD/INR"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data.get("conversion_rate"):
            rate = data["conversion_rate"]
            return f"📈 The current USD to INR rate is ₹{rate:.2f}"
        else:
            return "⚠️ Unable to fetch the latest exchange rate at the moment."
    else:
        return "🤖 I can help with USD to INR exchange rates. Try asking about the latest rate."
