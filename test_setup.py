#!/usr/bin/env python3
"""
Test setup script for USD/INR Trading Bot
This script tests if your API keys are properly configured.
"""

import os
import sys
from data_fetcher import (
    get_current_rate_with_fallback,
    get_alphavantage_intraday_data,
    get_live_candlestick_data
)

def test_alpha_vantage_api():
    """Test Alpha Vantage API key"""
    print("🔍 Testing Alpha Vantage API...")
    
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("❌ ALPHA_VANTAGE_API_KEY not found in environment variables")
        print("   Please set it using: export ALPHA_VANTAGE_API_KEY='your_key_here'")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        # Test current rate
        print("   Testing current USD/INR rate...")
        rate = get_current_rate_with_fallback()
        print(f"   ✅ Current rate: ₹{rate:.2f}")
        
        # Test intraday data
        print("   Testing intraday data (5min)...")
        data = get_live_candlestick_data(timeframe='5min', data_source='alphavantage')
        print(f"   ✅ Intraday data: {len(data)} data points")
        print(f"   ✅ Latest price: ₹{data['Close'].iloc[-1]:.2f}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_huggingface_api():
    """Test HuggingFace API key"""
    print("\n🔍 Testing HuggingFace API...")
    
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("❌ HF_TOKEN not found in environment variables")
        print("   Please set it using: export HF_TOKEN='your_token_here'")
        return False
    
    print(f"✅ HF Token found: {hf_token[:8]}...{hf_token[-4:]}")
    
    try:
        from langchain_community.llms import HuggingFaceHub
        
        llm = HuggingFaceHub(
            repo_id="HuggingFaceTB/SmolLM3-3B",
            huggingfacehub_api_token=hf_token,
            model_kwargs={"temperature": 0.7, "max_new_tokens": 100}
        )
        
        print("   Testing LLM response...")
        response = llm("What is forex trading?")
        print(f"   ✅ LLM Response: {response[:100]}...")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_yfinance_fallback():
    """Test Yahoo Finance fallback"""
    print("\n🔍 Testing Yahoo Finance fallback...")
    
    try:
        from data_fetcher import get_yfinance_candlestick_data
        
        data = get_yfinance_candlestick_data(symbol="USDINR=X", period="5d", interval="1d")
        print(f"   ✅ Yahoo Finance data: {len(data)} data points")
        print(f"   ✅ Latest price: ₹{data['Close'].iloc[-1]:.2f}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 USD/INR Trading Bot - Setup Test")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    # Test Alpha Vantage
    if test_alpha_vantage_api():
        success_count += 1
    
    # Test HuggingFace
    if test_huggingface_api():
        success_count += 1
    
    # Test Yahoo Finance fallback
    if test_yfinance_fallback():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! You're ready to run the trading bot.")
        print("   Run: streamlit run streamlit_app.py")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("   The app may still work with partial functionality.")
    
    print("\n💡 Tips:")
    print("   • For intraday data, Alpha Vantage API key is required")
    print("   • For AI chat, HuggingFace token is required")
    print("   • Yahoo Finance works without API key (daily data only)")
    print("   • Check README.md for detailed setup instructions")

if __name__ == "__main__":
    main()