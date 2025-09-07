from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    updated_timestamp = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Ticker(Base):
    __tablename__ = "tickers"
    
    ticker_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(16), unique=True, nullable=False)
    company_name = Column(String(256))
    sector = Column(String(128))
    industry = Column(String(128))
    created_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    updated_timestamp = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Portfolio(Base):
    __tablename__ = "portfolios"
    
    portfolio_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable=False)
    base_currency = Column(String(8), nullable=False, default='USD')
    created_by = Column(String, ForeignKey('users.user_id'), nullable=False)
    created_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    updated_timestamp = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    holdings = relationship("HoldingCurrent", back_populates="portfolio", cascade="all, delete-orphan")


class HoldingCurrent(Base):
    __tablename__ = "holdings_current"
    
    holding_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String, ForeignKey('portfolios.portfolio_id', ondelete='CASCADE'), nullable=False)
    ticker_id = Column(String, ForeignKey('tickers.ticker_id', ondelete='RESTRICT'), nullable=False)
    quantity = Column(Numeric(24, 8), nullable=False, default=0)
    market_value = Column(Numeric(24, 8), nullable=False, default=0)
    weight_pct = Column(Numeric(8, 4))
    updated_timestamp = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    ticker = relationship("Ticker")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('portfolio_id', 'ticker_id', name='uq_hc_portfolio_ticker'),
    )


class PriceDaily(Base):
    __tablename__ = "prices_daily"
    
    ticker_id = Column(String, ForeignKey('tickers.ticker_id', ondelete='CASCADE'), nullable=False, primary_key=True)
    date = Column(String, nullable=False, primary_key=True)  # Using String for date to match the schema
    close = Column(Numeric(20, 6), nullable=False)
