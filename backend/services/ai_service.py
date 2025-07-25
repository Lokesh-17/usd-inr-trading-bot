import os
from typing import Dict, List
import asyncio
import aiohttp
from datetime import datetime

class AIService:
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        self.model_id = "HuggingFaceTB/SmolLM3-3B"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        
        if not self.hf_token:
            print("WARNING: HF_TOKEN environment variable is not set.")
    
    async def get_response(self, user_message: str, current_rate: float = None) -> str:
        """Get AI response to user message with forex context"""
        if not self.hf_token:
            raise ValueError("HF_TOKEN is not set.")
        
        # Build context-aware prompt
        context = self._build_context(current_rate)
        prompt = f"{context}\n\nHuman: {user_message}\nAI:"
        
        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 256,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.api_url, headers=headers, json=payload) as response:
                    if response.status == 503:
                        # Model is loading, wait and retry
                        await asyncio.sleep(20)
                        async with session.post(self.api_url, headers=headers, json=payload) as retry_response:
                            retry_response.raise_for_status()
                            result = await retry_response.json()
                    else:
                        response.raise_for_status()
                        result = await response.json()
                    
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get("generated_text", "").strip()
                        return generated_text if generated_text else "I'm sorry, I couldn't generate a response at the moment."
                    else:
                        return "I'm sorry, I couldn't generate a response at the moment."
                        
            except aiohttp.ClientError as e:
                print(f"Error calling HuggingFace API: {e}")
                return self._get_fallback_response(user_message, current_rate)
            except Exception as e:
                print(f"Unexpected error in AI service: {e}")
                return self._get_fallback_response(user_message, current_rate)
    
    def _build_context(self, current_rate: float = None) -> str:
        """Build context for the AI model"""
        context = """You are a helpful AI assistant specialized in USD to INR exchange rates and forex trading.
You can analyze market trends, provide trading insights, and answer questions about currency exchange.
Keep your responses concise, informative, and helpful."""
        
        if current_rate:
            context += f"\n\nCurrent USD to INR exchange rate: ₹{current_rate:.2f}"
        
        return context
    
    def _get_fallback_response(self, user_message: str, current_rate: float = None) -> str:
        """Provide fallback response when AI service is unavailable"""
        message_lower = user_message.lower()
        
        if any(keyword in message_lower for keyword in ["price", "rate", "current", "usd", "inr"]):
            if current_rate:
                return f"📈 The current USD to INR exchange rate is ₹{current_rate:.2f}. The rate fluctuates based on various economic factors including market sentiment, economic indicators, and geopolitical events."
            else:
                return "📈 I can help you with USD to INR exchange rates, but I'm unable to fetch the current rate at the moment. Please try again later."
        
        elif any(keyword in message_lower for keyword in ["trade", "trading", "buy", "sell"]):
            return "💹 For trading USD/INR, consider factors like market trends, economic indicators, and your risk tolerance. Always do thorough research before making trading decisions."
        
        elif any(keyword in message_lower for keyword in ["chart", "analysis", "technical"]):
            return "📊 Technical analysis involves studying price charts, trends, and indicators like moving averages to make trading decisions. Look for patterns and support/resistance levels."
        
        else:
            return "🤖 I'm here to help with USD to INR exchange rates and forex trading questions. Feel free to ask about current rates, trading strategies, or market analysis."
    
    async def analyze_trading_signals(self, chart_data: List[Dict]) -> str:
        """Analyze chart data and provide trading insights"""
        if not chart_data:
            return "No chart data available for analysis."
        
        latest_candle = chart_data[0]  # Most recent data
        price_trend = self._analyze_price_trend(chart_data[:10])  # Last 10 candles
        
        analysis = f"Based on the latest USD/INR data:\n"
        analysis += f"• Current price: ₹{latest_candle['close']:.2f}\n"
        analysis += f"• Price trend: {price_trend}\n"
        
        # Check for signals if available
        if 'signal' in latest_candle:
            analysis += f"• Latest signal: {latest_candle['signal']}\n"
        
        if 'sma_short' in latest_candle and 'sma_long' in latest_candle:
            if latest_candle['sma_short'] and latest_candle['sma_long']:
                sma_position = "above" if latest_candle['sma_short'] > latest_candle['sma_long'] else "below"
                analysis += f"• Short SMA is {sma_position} long SMA\n"
        
        return analysis
    
    def _analyze_price_trend(self, recent_data: List[Dict]) -> str:
        """Analyze recent price trend"""
        if len(recent_data) < 3:
            return "Insufficient data"
        
        prices = [candle['close'] for candle in recent_data]
        
        # Simple trend analysis
        if prices[0] > prices[2]:  # Current vs 2 periods ago
            if prices[0] > prices[1]:  # Current vs previous
                return "Strong uptrend"
            else:
                return "Uptrend with recent pullback"
        elif prices[0] < prices[2]:
            if prices[0] < prices[1]:
                return "Strong downtrend"
            else:
                return "Downtrend with recent bounce"
        else:
            return "Sideways/consolidating"