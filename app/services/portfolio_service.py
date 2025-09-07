from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models.models import Portfolio, HoldingCurrent, Ticker
from app.schemas.schemas import PortfolioCreate, PortfolioUpdate, HoldingCreate, HoldingUpdate


class PortfolioService:
    def __init__(self, db: Session):
        self.db = db

    def create_portfolio(self, portfolio: PortfolioCreate) -> Portfolio:
        db_portfolio = Portfolio(**portfolio.dict())
        self.db.add(db_portfolio)
        self.db.commit()
        self.db.refresh(db_portfolio)
        return db_portfolio

    def get_portfolios(self, user_id: str) -> List[Portfolio]:
        return self.db.query(Portfolio).filter(Portfolio.created_by == user_id).all()

    def get_portfolio(self, portfolio_id: str, user_id: str) -> Optional[Portfolio]:
        return self.db.query(Portfolio).filter(
            and_(Portfolio.portfolio_id == portfolio_id, Portfolio.created_by == user_id)
        ).first()

    def update_portfolio(self, portfolio_id: str, user_id: str, portfolio_update: PortfolioUpdate) -> Optional[Portfolio]:
        db_portfolio = self.get_portfolio(portfolio_id, user_id)
        if not db_portfolio:
            return None
        
        update_data = portfolio_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_portfolio, field, value)
        
        self.db.commit()
        self.db.refresh(db_portfolio)
        return db_portfolio

    def delete_portfolio(self, portfolio_id: str, user_id: str) -> bool:
        db_portfolio = self.get_portfolio(portfolio_id, user_id)
        if not db_portfolio:
            return False
        
        self.db.delete(db_portfolio)
        self.db.commit()
        return True

    def get_portfolio_stocks(self, portfolio_id: str, user_id: str) -> List[HoldingCurrent]:
        # First verify the portfolio belongs to the user
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return []
        
        return self.db.query(HoldingCurrent).filter(
            HoldingCurrent.portfolio_id == portfolio_id
        ).all()

    def add_stock_to_portfolio(self, portfolio_id: str, user_id: str, holding: HoldingCreate) -> Optional[HoldingCurrent]:
        # First verify the portfolio belongs to the user
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return None
        
        # Check if ticker exists
        ticker = self.db.query(Ticker).filter(Ticker.ticker_id == holding.ticker_id).first()
        if not ticker:
            return None
        
        # Check if holding already exists for this portfolio and ticker
        existing_holding = self.db.query(HoldingCurrent).filter(
            and_(
                HoldingCurrent.portfolio_id == portfolio_id,
                HoldingCurrent.ticker_id == holding.ticker_id
            )
        ).first()
        
        if existing_holding:
            # Update existing holding
            for field, value in holding.dict(exclude_unset=True).items():
                setattr(existing_holding, field, value)
            self.db.commit()
            self.db.refresh(existing_holding)
            return existing_holding
        else:
            # Create new holding
            db_holding = HoldingCurrent(
                portfolio_id=portfolio_id,
                **holding.dict()
            )
            self.db.add(db_holding)
            self.db.commit()
            self.db.refresh(db_holding)
            return db_holding

    def update_stock_in_portfolio(self, portfolio_id: str, user_id: str, holding_id: str, holding_update: HoldingUpdate) -> Optional[HoldingCurrent]:
        # First verify the portfolio belongs to the user
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return None
        
        db_holding = self.db.query(HoldingCurrent).filter(
            and_(
                HoldingCurrent.holding_id == holding_id,
                HoldingCurrent.portfolio_id == portfolio_id
            )
        ).first()
        
        if not db_holding:
            return None
        
        update_data = holding_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_holding, field, value)
        
        self.db.commit()
        self.db.refresh(db_holding)
        return db_holding

    def remove_stock_from_portfolio(self, portfolio_id: str, user_id: str, holding_id: str) -> bool:
        # First verify the portfolio belongs to the user
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return False
        
        db_holding = self.db.query(HoldingCurrent).filter(
            and_(
                HoldingCurrent.holding_id == holding_id,
                HoldingCurrent.portfolio_id == portfolio_id
            )
        ).first()
        
        if not db_holding:
            return False
        
        self.db.delete(db_holding)
        self.db.commit()
        return True
