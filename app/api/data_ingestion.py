"""
Data ingestion API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.services.data_ingestion import DataIngestionService
from app.services.data_scraper import DataScraper
from app.schemas.schemas import Portfolio

router = APIRouter(prefix="/data", tags=["data-ingestion"])

class IngestTickersRequest(BaseModel):
    tickers: List[str]

class CreateSamplePortfoliosRequest(BaseModel):
    user_id: str

class UpdatePricesRequest(BaseModel):
    tickers: List[str]

@router.post("/ingest/tickers")
def ingest_tickers(
    request: IngestTickersRequest,
    db: Session = Depends(get_db)
):
    """Ingest ticker data into the database"""
    try:
        service = DataIngestionService(db)
        tickers = service.ingest_tickers(request.tickers)
        
        return {
            "message": f"Successfully ingested {len(tickers)} tickers",
            "tickers": [
                {
                    "ticker_id": ticker.ticker_id,
                    "symbol": ticker.symbol,
                    "company_name": ticker.company_name,
                    "sector": ticker.sector,
                    "industry": ticker.industry
                }
                for ticker in tickers
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting tickers: {str(e)}"
        )

@router.post("/ingest/sample-portfolios")
def create_sample_portfolios(
    request: CreateSamplePortfoliosRequest,
    db: Session = Depends(get_db)
):
    """Create sample portfolios based on Capitol Hill trades"""
    try:
        service = DataIngestionService(db)
        portfolios = service.create_sample_portfolios(request.user_id)
        
        return {
            "message": f"Successfully created {len(portfolios)} sample portfolios",
            "portfolios": [
                {
                    "portfolio_id": portfolio.portfolio_id,
                    "name": portfolio.name,
                    "base_currency": portfolio.base_currency,
                    "created_by": portfolio.created_by
                }
                for portfolio in portfolios
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating sample portfolios: {str(e)}"
        )

@router.post("/ingest/update-prices")
def update_stock_prices(
    request: UpdatePricesRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update stock prices for given tickers"""
    try:
        service = DataIngestionService(db)
        results = service.update_stock_prices(request.tickers)
        
        successful = sum(1 for success in results.values() if success)
        failed = len(results) - successful
        
        return {
            "message": f"Updated prices for {successful} tickers, {failed} failed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating prices: {str(e)}"
        )

@router.get("/scrape/capitol-hill-trades")
def get_capitol_hill_trades(limit: int = 10):
    """Get recent Capitol Hill trades"""
    try:
        scraper = DataScraper()
        trades = scraper.scrape_capitol_hill_trades(limit)
        
        return {
            "message": f"Retrieved {len(trades)} Capitol Hill trades",
            "trades": trades
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scraping Capitol Hill trades: {str(e)}"
        )

@router.get("/scrape/stock-data/{ticker}")
def get_stock_data(ticker: str, period: str = "1mo"):
    """Get stock data for a specific ticker"""
    try:
        scraper = DataScraper()
        data = scraper.scrape_stock_data([ticker], period)
        
        if ticker not in data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticker {ticker} not found"
            )
        
        return {
            "message": f"Retrieved data for {ticker}",
            "data": data[ticker]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scraping stock data: {str(e)}"
        )

@router.get("/portfolios/{portfolio_id}/summary")
def get_portfolio_summary(portfolio_id: str, db: Session = Depends(get_db)):
    """Get portfolio summary with current values"""
    try:
        service = DataIngestionService(db)
        summary = service.get_portfolio_summary(portfolio_id)
        
        if "error" in summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=summary["error"]
            )
        
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting portfolio summary: {str(e)}"
        )

@router.get("/top-stocks")
def get_top_stocks(limit: int = 20):
    """Get list of top stocks"""
    try:
        scraper = DataScraper()
        stocks = scraper.get_top_stocks(limit)
        
        return {
            "message": f"Retrieved {len(stocks)} top stocks",
            "stocks": stocks
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting top stocks: {str(e)}"
        )
