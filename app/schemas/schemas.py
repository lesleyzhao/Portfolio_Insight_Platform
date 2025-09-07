from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# User schemas
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    user_id: UUID
    created_timestamp: datetime
    updated_timestamp: datetime

    class Config:
        from_attributes = True


# Ticker schemas
class TickerBase(BaseModel):
    symbol: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None


class TickerCreate(TickerBase):
    pass


class Ticker(TickerBase):
    ticker_id: UUID
    created_timestamp: datetime
    updated_timestamp: datetime

    class Config:
        from_attributes = True


# Portfolio schemas
class PortfolioBase(BaseModel):
    name: str
    base_currency: str = "USD"


class PortfolioCreate(PortfolioBase):
    created_by: UUID


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    base_currency: Optional[str] = None


class Portfolio(PortfolioBase):
    portfolio_id: UUID
    created_by: UUID
    created_timestamp: datetime
    updated_timestamp: datetime
    holdings: List["HoldingCurrent"] = []

    class Config:
        from_attributes = True


# Holding schemas
class HoldingBase(BaseModel):
    quantity: Decimal
    market_value: Optional[Decimal] = 0
    weight_pct: Optional[Decimal] = None


class HoldingCreate(HoldingBase):
    ticker_id: UUID


class HoldingUpdate(BaseModel):
    quantity: Optional[Decimal] = None
    market_value: Optional[Decimal] = None
    weight_pct: Optional[Decimal] = None


class HoldingCurrent(HoldingBase):
    holding_id: UUID
    portfolio_id: UUID
    ticker_id: UUID
    updated_timestamp: datetime
    ticker: Optional[Ticker] = None

    class Config:
        from_attributes = True


# Price schemas
class PriceDailyBase(BaseModel):
    date: str
    close: Decimal


class PriceDailyCreate(PriceDailyBase):
    ticker_id: UUID


class PriceDaily(PriceDailyBase):
    ticker_id: UUID

    class Config:
        from_attributes = True


# Update forward references
Portfolio.model_rebuild()
HoldingCurrent.model_rebuild()
