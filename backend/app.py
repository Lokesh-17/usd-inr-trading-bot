from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime
import os

from database import get_db, engine
from models import Base, User, Portfolio, Trade, ChatMessage
from schemas import (
    UserCreate, UserResponse, PortfolioResponse, TradeCreate, TradeResponse,
    ChatMessageCreate, ChatMessageResponse, ExchangeRateResponse
)
from services.forex_service import ForexService
from services.ai_service import AIService
from services.trading_service import TradingService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="USD/INR Trading Bot API", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
forex_service = ForexService()
ai_service = AIService()
trading_service = TradingService()

@app.get("/")
async def root():
    return {"message": "USD/INR Trading Bot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# User endpoints
@app.post("/api/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user with default portfolio"""
    db_user = trading_service.create_user(db, user)
    return db_user

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    db_user = trading_service.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Portfolio endpoints
@app.get("/api/users/{user_id}/portfolio", response_model=PortfolioResponse)
async def get_portfolio(user_id: int, db: Session = Depends(get_db)):
    """Get user's portfolio"""
    portfolio = trading_service.get_portfolio(db, user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

@app.post("/api/users/{user_id}/portfolio/reset")
async def reset_portfolio(user_id: int, db: Session = Depends(get_db)):
    """Reset user's portfolio to default values"""
    portfolio = trading_service.reset_portfolio(db, user_id)
    return {"message": "Portfolio reset successfully", "portfolio": portfolio}

# Trading endpoints
@app.post("/api/users/{user_id}/trades", response_model=TradeResponse)
async def execute_trade(user_id: int, trade: TradeCreate, db: Session = Depends(get_db)):
    """Execute a trade (buy/sell USD)"""
    try:
        current_rate = await forex_service.get_usd_inr_rate()
        trade_result = trading_service.execute_trade(db, user_id, trade, current_rate)
        return trade_result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/users/{user_id}/trades", response_model=List[TradeResponse])
async def get_trade_history(user_id: int, db: Session = Depends(get_db)):
    """Get user's trade history"""
    trades = trading_service.get_trade_history(db, user_id)
    return trades

# Forex endpoints
@app.get("/api/forex/usd-inr", response_model=ExchangeRateResponse)
async def get_exchange_rate():
    """Get current USD to INR exchange rate"""
    try:
        rate = await forex_service.get_usd_inr_rate()
        return {
            "from_currency": "USD",
            "to_currency": "INR",
            "rate": rate,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch exchange rate: {str(e)}")

@app.get("/api/forex/chart-data")
async def get_chart_data(interval: str = "5min", outputsize: str = "compact"):
    """Get candlestick chart data for USD/INR"""
    try:
        chart_data = await forex_service.get_candlestick_data(interval, outputsize)
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chart data: {str(e)}")

# Chat endpoints
@app.post("/api/users/{user_id}/chat", response_model=ChatMessageResponse)
async def send_chat_message(user_id: int, message: ChatMessageCreate, db: Session = Depends(get_db)):
    """Send a chat message and get AI response"""
    try:
        # Get current exchange rate for context
        current_rate = await forex_service.get_usd_inr_rate()
        
        # Generate AI response
        ai_response = await ai_service.get_response(message.content, current_rate)
        
        # Save both user message and AI response
        user_msg = trading_service.save_chat_message(db, user_id, message.content, "user")
        ai_msg = trading_service.save_chat_message(db, user_id, ai_response, "assistant")
        
        return ai_msg
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

@app.get("/api/users/{user_id}/chat", response_model=List[ChatMessageResponse])
async def get_chat_history(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Get user's chat history"""
    messages = trading_service.get_chat_history(db, user_id, limit)
    return messages

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)