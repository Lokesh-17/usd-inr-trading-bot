from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from enum import Enum

class TradeTypeEnum(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class MessageRoleEnum(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

# User schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Portfolio schemas
class PortfolioResponse(BaseModel):
    id: int
    user_id: int
    inr_balance: float
    usd_held: float
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Trade schemas
class TradeCreate(BaseModel):
    trade_type: TradeTypeEnum
    amount_usd: float

class TradeResponse(BaseModel):
    id: int
    user_id: int
    trade_type: TradeTypeEnum
    amount_usd: float
    exchange_rate: float
    amount_inr: float
    executed_at: datetime
    inr_balance_after: float
    usd_held_after: float
    
    class Config:
        from_attributes = True

# Chat schemas
class ChatMessageCreate(BaseModel):
    content: str

class ChatMessageResponse(BaseModel):
    id: int
    user_id: int
    role: MessageRoleEnum
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Forex schemas
class ExchangeRateResponse(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
    timestamp: datetime

class CandlestickData(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class ChartDataResponse(BaseModel):
    data: List[CandlestickData]
    interval: str
    symbol: str