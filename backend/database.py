from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from urllib.parse import quote_plus

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://trading_user:trading_password@localhost:5432/trading_bot_db"
)

# Handle special characters in password
if "://" in DATABASE_URL and "@" in DATABASE_URL:
    # Parse and encode password if needed
    parts = DATABASE_URL.split("://")[1]
    if "@" in parts:
        credentials, host_db = parts.split("@", 1)
        if ":" in credentials:
            username, password = credentials.split(":", 1)
            encoded_password = quote_plus(password)
            DATABASE_URL = f"{DATABASE_URL.split('://')[0]}://{username}:{encoded_password}@{host_db}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()