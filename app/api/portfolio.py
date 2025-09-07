from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.schemas import Portfolio, PortfolioCreate, PortfolioUpdate, HoldingCurrent, HoldingCreate, HoldingUpdate
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.post("/", response_model=Portfolio, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db)
):
    """Create a new portfolio"""
    service = PortfolioService(db)
    return service.create_portfolio(portfolio)


@router.get("/", response_model=List[Portfolio])
def get_portfolios(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all portfolios for a user"""
    service = PortfolioService(db)
    portfolios = service.get_portfolios(user_id)
    return portfolios


@router.get("/{portfolio_id}", response_model=Portfolio)
def get_portfolio(
    portfolio_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific portfolio by ID"""
    service = PortfolioService(db)
    portfolio = service.get_portfolio(portfolio_id, user_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    return portfolio


@router.put("/{portfolio_id}", response_model=Portfolio)
def update_portfolio(
    portfolio_id: str,
    user_id: str,
    portfolio_update: PortfolioUpdate,
    db: Session = Depends(get_db)
):
    """Update a portfolio"""
    service = PortfolioService(db)
    portfolio = service.update_portfolio(portfolio_id, user_id, portfolio_update)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(
    portfolio_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Delete a portfolio"""
    service = PortfolioService(db)
    success = service.delete_portfolio(portfolio_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )


@router.get("/{portfolio_id}/stocks", response_model=List[HoldingCurrent])
def get_portfolio_stocks(
    portfolio_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all stocks in a portfolio"""
    service = PortfolioService(db)
    stocks = service.get_portfolio_stocks(portfolio_id, user_id)
    if stocks is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    return stocks


@router.post("/{portfolio_id}/stocks", response_model=HoldingCurrent, status_code=status.HTTP_201_CREATED)
def add_stock_to_portfolio(
    portfolio_id: str,
    user_id: str,
    holding: HoldingCreate,
    db: Session = Depends(get_db)
):
    """Add a stock to a portfolio"""
    service = PortfolioService(db)
    result = service.add_stock_to_portfolio(portfolio_id, user_id, holding)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio or ticker not found"
        )
    return result


@router.patch("/{portfolio_id}/stocks/{holding_id}", response_model=HoldingCurrent)
def update_stock_in_portfolio(
    portfolio_id: str,
    user_id: str,
    holding_id: str,
    holding_update: HoldingUpdate,
    db: Session = Depends(get_db)
):
    """Update a stock holding in a portfolio"""
    service = PortfolioService(db)
    result = service.update_stock_in_portfolio(portfolio_id, user_id, holding_id, holding_update)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio or holding not found"
        )
    return result


@router.delete("/{portfolio_id}/stocks/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_stock_from_portfolio(
    portfolio_id: str,
    user_id: str,
    holding_id: str,
    db: Session = Depends(get_db)
):
    """Remove a stock from a portfolio"""
    service = PortfolioService(db)
    success = service.remove_stock_from_portfolio(portfolio_id, user_id, holding_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio or holding not found"
        )
