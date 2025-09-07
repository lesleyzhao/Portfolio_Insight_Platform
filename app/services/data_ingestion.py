"""
Data ingestion service for storing scraped data in the database
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, date
import logging
import pandas as pd

from app.models.models import Ticker, Portfolio, HoldingCurrent, PriceDaily, User
from app.services.data_scraper import DataScraper
from app.schemas.schemas import PortfolioCreate, HoldingCreate

logger = logging.getLogger(__name__)

class DataIngestionService:
    """Service for ingesting scraped data into the database"""
    
    def __init__(self, db: Session):
        self.db = db
        self.scraper = DataScraper()
    
    def ingest_tickers(self, tickers: List[str]) -> List[Ticker]:
        """
        Ingest ticker data into the database
        """
        created_tickers = []
        
        for ticker_symbol in tickers:
            try:
                # Check if ticker already exists
                existing_ticker = self.db.query(Ticker).filter(Ticker.symbol == ticker_symbol).first()
                if existing_ticker:
                    logger.info(f"Ticker {ticker_symbol} already exists")
                    created_tickers.append(existing_ticker)
                    continue
                
                # Scrape ticker data
                stock_data = self.scraper.scrape_stock_data([ticker_symbol])
                data = stock_data.get(ticker_symbol, {})
                
                if "error" in data:
                    logger.error(f"Error scraping {ticker_symbol}: {data['error']}")
                    continue
                
                # Create ticker record
                ticker = Ticker(
                    symbol=ticker_symbol,
                    company_name=data.get("company_name", ticker_symbol),
                    sector=data.get("sector", "Unknown"),
                    industry=data.get("industry", "Unknown")
                )
                
                self.db.add(ticker)
                self.db.flush()  # Get the ID
                
                # Store historical price data
                if data.get("historical_data"):
                    self._store_price_data(ticker.ticker_id, data["historical_data"])
                
                created_tickers.append(ticker)
                logger.info(f"Created ticker {ticker_symbol}")
                
            except Exception as e:
                logger.error(f"Error ingesting ticker {ticker_symbol}: {e}")
                continue
        
        self.db.commit()
        return created_tickers
    
    def _store_price_data(self, ticker_id: str, historical_data: List[Dict]):
        """
        Store historical price data
        """
        try:
            for record in historical_data:
                # Convert date to string for SQLite compatibility
                record_date = record.get('Date')
                if isinstance(record_date, pd.Timestamp):
                    record_date = record_date.strftime('%Y-%m-%d')
                elif hasattr(record_date, 'date'):
                    record_date = record_date.date().strftime('%Y-%m-%d')
                
                price_record = PriceDaily(
                    ticker_id=ticker_id,
                    date=record_date,
                    close=float(record.get('Close', 0))
                )
                
                # Use merge to handle duplicates
                self.db.merge(price_record)
            
            logger.info(f"Stored {len(historical_data)} price records for ticker {ticker_id}")
            
        except Exception as e:
            logger.error(f"Error storing price data: {e}")
    
    def create_sample_portfolios(self, user_id: str) -> List[Portfolio]:
        """
        Create sample portfolios based on Capitol Hill trades
        """
        try:
            # Get Capitol Hill trades
            trades = self.scraper.scrape_capitol_hill_trades()
            
            if not trades:
                logger.warning("No Capitol Hill trades found")
                return []
            
            # Extract unique tickers from trades
            ticker_symbols = list(set([trade["ticker"] for trade in trades]))
            
            # Ingest tickers first
            tickers = self.ingest_tickers(ticker_symbols)
            ticker_map = {ticker.symbol: ticker for ticker in tickers}
            
            # Create portfolios based on trades
            portfolios = []
            
            # Group trades by actor to create portfolios
            actor_trades = {}
            for trade in trades:
                actor = trade["actor"]
                if actor not in actor_trades:
                    actor_trades[actor] = []
                actor_trades[actor].append(trade)
            
            for actor, actor_trade_list in actor_trades.items():
                # Create portfolio for this actor
                portfolio = Portfolio(
                    name=f"{actor}'s Portfolio",
                    base_currency="USD",
                    created_by=user_id
                )
                
                self.db.add(portfolio)
                self.db.flush()  # Get the ID
                
                # Add holdings based on trades
                for trade in actor_trade_list:
                    ticker_symbol = trade["ticker"]
                    if ticker_symbol in ticker_map:
                        ticker = ticker_map[ticker_symbol]
                        
                        # Calculate current market value
                        current_price = trade["price"]  # Use trade price as current price
                        quantity = trade["quantity"]
                        market_value = current_price * quantity
                        
                        # Calculate weight (simplified - equal weight for demo)
                        total_value = sum(t["price"] * t["quantity"] for t in actor_trade_list)
                        weight_pct = (market_value / total_value) * 100 if total_value > 0 else 0
                        
                        holding = HoldingCurrent(
                            portfolio_id=portfolio.portfolio_id,
                            ticker_id=ticker.ticker_id,
                            quantity=quantity,
                            market_value=market_value,
                            weight_pct=weight_pct
                        )
                        
                        self.db.add(holding)
                
                portfolios.append(portfolio)
                logger.info(f"Created portfolio for {actor} with {len(actor_trade_list)} holdings")
            
            self.db.commit()
            return portfolios
            
        except Exception as e:
            logger.error(f"Error creating sample portfolios: {e}")
            self.db.rollback()
            return []
    
    def update_stock_prices(self, ticker_symbols: List[str]) -> Dict[str, bool]:
        """
        Update current stock prices for given tickers
        """
        results = {}
        
        try:
            # Scrape current data
            stock_data = self.scraper.scrape_stock_data(ticker_symbols, period="5d")
            
            for symbol, data in stock_data.items():
                try:
                    if "error" in data:
                        results[symbol] = False
                        continue
                    
                    # Find ticker in database
                    ticker = self.db.query(Ticker).filter(Ticker.symbol == symbol).first()
                    if not ticker:
                        logger.warning(f"Ticker {symbol} not found in database")
                        results[symbol] = False
                        continue
                    
                    # Update current price data
                    if data.get("historical_data"):
                        self._store_price_data(ticker.ticker_id, data["historical_data"])
                    
                    # Update holdings with current prices
                    holdings = self.db.query(HoldingCurrent).filter(
                        HoldingCurrent.ticker_id == ticker.ticker_id
                    ).all()
                    
                    current_price = data.get("current_price")
                    if current_price:
                        for holding in holdings:
                            holding.market_value = current_price * float(holding.quantity)
                            # Recalculate weight
                            portfolio = self.db.query(Portfolio).filter(
                                Portfolio.portfolio_id == holding.portfolio_id
                            ).first()
                            if portfolio:
                                total_value = sum(h.market_value for h in portfolio.holdings)
                                if total_value > 0:
                                    holding.weight_pct = (holding.market_value / total_value) * 100
                    
                    results[symbol] = True
                    logger.info(f"Updated prices for {symbol}")
                    
                except Exception as e:
                    logger.error(f"Error updating prices for {symbol}: {e}")
                    results[symbol] = False
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating stock prices: {e}")
            self.db.rollback()
        
        return results
    
    def get_portfolio_summary(self, portfolio_id: str) -> Dict:
        """
        Get portfolio summary with current values
        """
        try:
            portfolio = self.db.query(Portfolio).filter(
                Portfolio.portfolio_id == portfolio_id
            ).first()
            
            if not portfolio:
                return {"error": "Portfolio not found"}
            
            holdings = self.db.query(HoldingCurrent).filter(
                HoldingCurrent.portfolio_id == portfolio_id
            ).all()
            
            total_value = sum(float(h.market_value) for h in holdings)
            
            summary = {
                "portfolio_id": portfolio_id,
                "name": portfolio.name,
                "total_value": total_value,
                "holdings_count": len(holdings),
                "holdings": []
            }
            
            for holding in holdings:
                ticker = self.db.query(Ticker).filter(
                    Ticker.ticker_id == holding.ticker_id
                ).first()
                
                if ticker:
                    summary["holdings"].append({
                        "symbol": ticker.symbol,
                        "company_name": ticker.company_name,
                        "quantity": float(holding.quantity),
                        "market_value": float(holding.market_value),
                        "weight_pct": float(holding.weight_pct) if holding.weight_pct else 0
                    })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {"error": str(e)}
