"""
Enhanced price data models for different time intervals
"""
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.database import Base

class PriceHourly(Base):
    """Hourly price data"""
    __tablename__ = "prices_hourly"
    
    ticker_id = Column(String, ForeignKey('tickers.ticker_id', ondelete='CASCADE'), nullable=False, primary_key=True)
    timestamp = Column(DateTime, nullable=False, primary_key=True)
    open = Column(Numeric(20, 6))
    high = Column(Numeric(20, 6))
    low = Column(Numeric(20, 6))
    close = Column(Numeric(20, 6), nullable=False)
    volume = Column(Numeric(20, 0))
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_hourly_ticker_timestamp', 'ticker_id', 'timestamp'),
    )

class PriceMinute(Base):
    """Minute-level price data (for real-time trading)"""
    __tablename__ = "prices_minute"
    
    ticker_id = Column(String, ForeignKey('tickers.ticker_id', ondelete='CASCADE'), nullable=False, primary_key=True)
    timestamp = Column(DateTime, nullable=False, primary_key=True)
    open = Column(Numeric(20, 6))
    high = Column(Numeric(20, 6))
    low = Column(Numeric(20, 6))
    close = Column(Numeric(20, 6), nullable=False)
    volume = Column(Numeric(20, 0))
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_minute_ticker_timestamp', 'ticker_id', 'timestamp'),
    )

class PriceSecond(Base):
    """Second-level price data (for high-frequency trading)"""
    __tablename__ = "prices_second"
    
    ticker_id = Column(String, ForeignKey('tickers.ticker_id', ondelete='CASCADE'), nullable=False, primary_key=True)
    timestamp = Column(DateTime, nullable=False, primary_key=True)
    open = Column(Numeric(20, 6))
    high = Column(Numeric(20, 6))
    low = Column(Numeric(20, 6))
    close = Column(Numeric(20, 6), nullable=False)
    volume = Column(Numeric(20, 0))
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_second_ticker_timestamp', 'ticker_id', 'timestamp'),
    )

class PriceRealTime(Base):
    """Real-time price data (latest prices)"""
    __tablename__ = "prices_realtime"
    
    ticker_id = Column(String, ForeignKey('tickers.ticker_id', ondelete='CASCADE'), nullable=False, primary_key=True)
    last_updated = Column(DateTime, nullable=False)
    price = Column(Numeric(20, 6), nullable=False)
    change = Column(Numeric(20, 6))  # Price change from previous close
    change_percent = Column(Numeric(8, 4))  # Percentage change
    volume = Column(Numeric(20, 0))
    market_cap = Column(Numeric(20, 0))
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_realtime_ticker', 'ticker_id'),
    )
