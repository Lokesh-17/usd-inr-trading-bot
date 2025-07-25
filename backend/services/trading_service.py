from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from models import User, Portfolio, Trade, ChatMessage, TradeType, MessageRole
from schemas import UserCreate, TradeCreate

class TradingService:
    def create_user(self, db: Session, user: UserCreate) -> User:
        """Create a new user with default portfolio"""
        # Create user
        db_user = User(
            username=user.username,
            email=user.email
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create default portfolio
        db_portfolio = Portfolio(
            user_id=db_user.id,
            inr_balance=100000.0,  # Default 1 lakh INR
            usd_held=0.0
        )
        db.add(db_portfolio)
        db.commit()
        
        return db_user
    
    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    def get_portfolio(self, db: Session, user_id: int) -> Optional[Portfolio]:
        """Get user's portfolio"""
        return db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
    
    def reset_portfolio(self, db: Session, user_id: int) -> Portfolio:
        """Reset user's portfolio to default values"""
        portfolio = self.get_portfolio(db, user_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        portfolio.inr_balance = 100000.0
        portfolio.usd_held = 0.0
        portfolio.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(portfolio)
        
        return portfolio
    
    def execute_trade(self, db: Session, user_id: int, trade: TradeCreate, current_rate: float) -> Trade:
        """Execute a trade (buy/sell USD)"""
        portfolio = self.get_portfolio(db, user_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        amount_inr = trade.amount_usd * current_rate
        
        if trade.trade_type == TradeType.BUY:
            # Buy USD with INR
            if portfolio.inr_balance < amount_inr:
                raise ValueError("Insufficient INR balance")
            
            portfolio.inr_balance -= amount_inr
            portfolio.usd_held += trade.amount_usd
            
        elif trade.trade_type == TradeType.SELL:
            # Sell USD for INR
            if portfolio.usd_held < trade.amount_usd:
                raise ValueError("Insufficient USD holdings")
            
            portfolio.inr_balance += amount_inr
            portfolio.usd_held -= trade.amount_usd
        
        else:
            raise ValueError("Invalid trade type")
        
        portfolio.updated_at = datetime.utcnow()
        
        # Create trade record
        db_trade = Trade(
            user_id=user_id,
            trade_type=trade.trade_type,
            amount_usd=trade.amount_usd,
            exchange_rate=current_rate,
            amount_inr=amount_inr,
            inr_balance_after=portfolio.inr_balance,
            usd_held_after=portfolio.usd_held
        )
        
        db.add(db_trade)
        db.commit()
        db.refresh(db_trade)
        
        return db_trade
    
    def get_trade_history(self, db: Session, user_id: int, limit: int = 50) -> List[Trade]:
        """Get user's trade history"""
        return (db.query(Trade)
                .filter(Trade.user_id == user_id)
                .order_by(Trade.executed_at.desc())
                .limit(limit)
                .all())
    
    def save_chat_message(self, db: Session, user_id: int, content: str, role: str) -> ChatMessage:
        """Save a chat message"""
        message_role = MessageRole.USER if role == "user" else MessageRole.ASSISTANT
        
        db_message = ChatMessage(
            user_id=user_id,
            role=message_role,
            content=content
        )
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        return db_message
    
    def get_chat_history(self, db: Session, user_id: int, limit: int = 50) -> List[ChatMessage]:
        """Get user's chat history"""
        return (db.query(ChatMessage)
                .filter(ChatMessage.user_id == user_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(limit)
                .all())
    
    def get_portfolio_value(self, db: Session, user_id: int, current_rate: float) -> dict:
        """Calculate total portfolio value in INR"""
        portfolio = self.get_portfolio(db, user_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        usd_value_inr = portfolio.usd_held * current_rate
        total_value_inr = portfolio.inr_balance + usd_value_inr
        
        return {
            "inr_balance": portfolio.inr_balance,
            "usd_held": portfolio.usd_held,
            "usd_value_inr": usd_value_inr,
            "total_value_inr": total_value_inr,
            "current_rate": current_rate
        }