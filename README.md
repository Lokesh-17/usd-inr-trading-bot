# 💹 USD/INR Trading Bot with Live Intraday Charts

A comprehensive Streamlit-based trading bot that provides real-time USD/INR exchange rate monitoring, intraday candlestick charts, SMA-based trading signals, virtual portfolio management, and an AI-powered chatbot assistant.

## ✨ Features

### 🔥 NEW: Live Intraday Charts
- **True intraday data** for USD/INR using Alpha Vantage API
- **Multiple timeframes**: 1min, 5min, 15min, 30min, 60min, and daily
- **Auto-refresh capability** with customizable intervals
- **Dynamic Y-axis scaling** for optimal chart viewing
- **Fallback mechanism** to Yahoo Finance for reliability

### 📊 Trading Features
- **SMA-based trading signals** with customizable periods
- **Virtual portfolio management** with INR/USD tracking
- **Real-time portfolio valuation** at current exchange rates
- **Trade simulation** with buy/sell signal execution
- **Historical trade tracking** with detailed logs

### 🤖 AI Assistant
- **LLM-powered chatbot** using HuggingFace SmolLM3-3B
- **Forex market insights** and trading advice
- **Real-time rate queries** with live data integration
- **Conversational memory** for context-aware responses

### 🎨 Modern UI
- **Responsive design** with sidebar controls
- **Real-time metrics** and portfolio displays
- **Interactive charts** with Plotly integration
- **Wide layout** optimized for trading dashboards

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd usd-inr-trading-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up API Keys

#### Alpha Vantage API Key (Required for Intraday Data)
1. Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Sign up for a free account
3. Get your API key
4. Set the environment variable:

**Linux/Mac:**
```bash
export ALPHA_VANTAGE_API_KEY="your_api_key_here"
```

**Windows:**
```cmd
set ALPHA_VANTAGE_API_KEY=your_api_key_here
```

#### HuggingFace API Key (Required for AI Chat)
1. Visit [HuggingFace](https://huggingface.co/settings/tokens)
2. Create a new token
3. Set the environment variable:

**Linux/Mac:**
```bash
export HF_TOKEN="your_huggingface_token_here"
```

**Windows:**
```cmd
set HF_TOKEN=your_huggingface_token_here
```

### 4. Run the Application
```bash
streamlit run streamlit_app.py
```

## 🔧 Configuration

### Data Sources
- **Alpha Vantage (Recommended)**: Provides true intraday USD/INR data
- **Yahoo Finance**: Fallback for daily data when Alpha Vantage is unavailable

### Timeframes
- **1 Minute**: Ultra-short term analysis
- **5 Minutes**: Short-term trading signals
- **15 Minutes**: Medium-term patterns
- **30 Minutes**: Balanced view
- **60 Minutes**: Hourly trends
- **Daily**: Long-term analysis

### SMA Settings
- **Short SMA**: 5-50 periods (default: 20)
- **Long SMA**: 20-200 periods (default: 50)
- **Signals**: Generated on SMA crossovers

### Auto-refresh
- **Intraday**: 30-300 seconds (default: 60s)
- **Daily**: 300-3600 seconds (default: 600s)

## 📈 Trading Logic

### Signal Generation
- **Buy Signal**: Short SMA crosses above Long SMA
- **Sell Signal**: Short SMA crosses below Long SMA

### Portfolio Management
- **Starting Balance**: ₹100,000 INR
- **Trade Amount**: ₹10,000 per trade
- **Position**: Buy/Sell all USD on signals
- **Valuation**: Real-time at current exchange rates

### Risk Management
- **Virtual Trading**: No real money involved
- **Position Limits**: Maximum trade amount enforced
- **Reset Function**: Restart portfolio anytime

## 🛠 Technical Stack

- **Frontend**: Streamlit
- **Charts**: Plotly (interactive candlestick charts)
- **Data Sources**: Alpha Vantage API, Yahoo Finance
- **AI Model**: HuggingFace SmolLM3-3B
- **Languages**: Python 3.8+

## 📋 API Limits

### Alpha Vantage (Free Tier)
- **25 API calls per day**
- **500 API calls per month**
- **5 API calls per minute**

### HuggingFace (Free Tier)
- **Generous limits** for inference API
- **Rate limiting** may apply during peak usage

## 🚨 Troubleshooting

### Common Issues

1. **"ALPHA_VANTAGE_API_KEY not found"**
   - Ensure the environment variable is set correctly
   - Restart your terminal/IDE after setting the variable

2. **"Failed to fetch intraday data"**
   - Check your Alpha Vantage API key is valid
   - Verify you haven't exceeded API limits
   - App will automatically fallback to Yahoo Finance

3. **"HuggingFace token error"**
   - Verify your HF_TOKEN is correct
   - Ensure the token has appropriate permissions

4. **Chart not updating**
   - Check your internet connection
   - Verify API keys are working
   - Try refreshing the page

### Performance Tips
- Use longer timeframes during high-traffic periods
- Adjust refresh intervals based on your needs
- Monitor API usage to avoid limits

## 🔄 Deployment to Streamlit Cloud

1. **Fork/Clone** this repository to your GitHub account

2. **Set up Streamlit Cloud account** at [share.streamlit.io](https://share.streamlit.io)

3. **Deploy** your app by connecting to your GitHub repository

4. **Configure secrets** in Streamlit Cloud:
   - Go to your app settings
   - Add secrets:
     ```toml
     ALPHA_VANTAGE_API_KEY = "your_api_key_here"
     HF_TOKEN = "your_huggingface_token_here"
     ```

5. **Deploy** and your app will be live!

## 🔮 Future Enhancements

- [ ] Multiple currency pairs support
- [ ] Advanced technical indicators (RSI, MACD, Bollinger Bands)
- [ ] Email/SMS notifications for trading signals
- [ ] Historical backtesting with different strategies
- [ ] Real broker integration (paper trading)
- [ ] Machine learning price prediction
- [ ] Custom indicator development

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This trading bot is for educational and simulation purposes only. It uses virtual money and should not be considered as financial advice. Always do your own research and consult with financial professionals before making real investment decisions.

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Email**: [Your email for support]

---

**Made with ❤️ for the trading community**