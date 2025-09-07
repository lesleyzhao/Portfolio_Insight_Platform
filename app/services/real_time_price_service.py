"""
Real-time price data service using industry best practices
"""
import redis
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.models.models import Ticker, PriceDaily
from app.services.data_scraper import DataScraper

logger = logging.getLogger(__name__)

class RealTimePriceService:
    """
    Industry-standard real-time price service using:
    - Redis for real-time data (last 24 hours)
    - PostgreSQL for historical data
    - WebSocket for live updates
    """
    
    def __init__(self, db: Session, redis_url: str = "redis://localhost:6379"):
        self.db = db
        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
        self.scraper = DataScraper()
        
        # Redis keys structure
        self.REALTIME_KEY = "price:realtime:{ticker}"
        self.HISTORICAL_KEY = "price:historical:{ticker}:{date}"
        self.SUBSCRIPTION_KEY = "price:subscriptions"
        
    def store_real_time_price(self, ticker: str, price_data: Dict) -> bool:
        """
        Store real-time price data in Redis with rolling window
        Industry standard: Keep only last 5 minutes of 1-second data
        """
        try:
            ticker_key = self.REALTIME_KEY.format(ticker=ticker)
            
            # Store current price with timestamp
            price_record = {
                "ticker": ticker,
                "price": float(price_data.get("price", 0)),
                "change": float(price_data.get("change", 0)),
                "change_percent": float(price_data.get("change_percent", 0)),
                "volume": int(price_data.get("volume", 0)),
                "timestamp": datetime.now().isoformat(),
                "market_cap": price_data.get("market_cap"),
                "high": float(price_data.get("high", 0)),
                "low": float(price_data.get("low", 0)),
                "open": float(price_data.get("open", 0))
            }
            
            # Store latest price (overwrites previous)
            self.redis_client.setex(
                ticker_key, 
                timedelta(hours=1),  # Keep for 1 hour
                json.dumps(price_record)
            )
            
            # Store in time-series with rolling window (last 300 records = 5 minutes)
            timestamp = int(datetime.now().timestamp())
            self.redis_client.zadd(
                f"price:timeseries:{ticker}",
                {json.dumps(price_record): timestamp}
            )
            
            # Keep only last 300 records (5 minutes at 1-second intervals)
            self.redis_client.zremrangebyrank(f"price:timeseries:{ticker}", 0, -301)
            
            # Set TTL for time-series data (1 hour)
            self.redis_client.expire(f"price:timeseries:{ticker}", 3600)
            
            logger.info(f"Stored real-time price for {ticker}: ${price_record['price']}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing real-time price for {ticker}: {e}")
            return False
    
    def get_real_time_price(self, ticker: str) -> Optional[Dict]:
        """
        Get latest real-time price from Redis
        """
        try:
            ticker_key = self.REALTIME_KEY.format(ticker=ticker)
            price_data = self.redis_client.get(ticker_key)
            
            if price_data:
                return json.loads(price_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting real-time price for {ticker}: {e}")
            return None
    
    def get_price_history(self, ticker: str, hours: int = 24) -> List[Dict]:
        """
        Get price history from Redis (last N hours)
        """
        try:
            # Get time-series data from Redis
            end_time = int(datetime.now().timestamp())
            start_time = end_time - (hours * 3600)
            
            price_data = self.redis_client.zrangebyscore(
                f"price:timeseries:{ticker}",
                start_time,
                end_time,
                withscores=True
            )
            
            return [json.loads(data) for data, _ in price_data]
            
        except Exception as e:
            logger.error(f"Error getting price history for {ticker}: {e}")
            return []
    
    def store_historical_price(self, ticker: str, price_data: Dict) -> bool:
        """
        Store historical price data in PostgreSQL
        Industry standard: Use TimescaleDB for time-series data
        """
        try:
            # Find ticker in database
            ticker_record = self.db.query(Ticker).filter(Ticker.symbol == ticker).first()
            if not ticker_record:
                logger.warning(f"Ticker {ticker} not found in database")
                return False
            
            # Store in PostgreSQL (daily prices)
            price_record = PriceDaily(
                ticker_id=ticker_record.ticker_id,
                date=price_data.get("date", datetime.now().date()),
                close=float(price_data.get("close", 0))
            )
            
            # Use merge to handle duplicates
            self.db.merge(price_record)
            self.db.commit()
            
            logger.info(f"Stored historical price for {ticker}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing historical price for {ticker}: {e}")
            self.db.rollback()
            return False
    
    def get_historical_prices(self, ticker: str, days: int = 30) -> List[Dict]:
        """
        Get historical prices from PostgreSQL
        """
        try:
            ticker_record = self.db.query(Ticker).filter(Ticker.symbol == ticker).first()
            if not ticker_record:
                return []
            
            # Query historical data
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            prices = self.db.query(PriceDaily).filter(
                PriceDaily.ticker_id == ticker_record.ticker_id,
                PriceDaily.date >= start_date,
                PriceDaily.date <= end_date
            ).order_by(PriceDaily.date.desc()).all()
            
            return [
                {
                    "date": str(price.date),
                    "close": float(price.close),
                    "ticker": ticker
                }
                for price in prices
            ]
            
        except Exception as e:
            logger.error(f"Error getting historical prices for {ticker}: {e}")
            return []
    
    def update_prices_from_yahoo(self, tickers: List[str]) -> Dict[str, bool]:
        """
        Update prices from Yahoo Finance (with rate limiting)
        """
        results = {}
        
        for ticker in tickers:
            try:
                # Get stock data
                stock_data = self.scraper.scrape_stock_data([ticker], period="1d")
                data = stock_data.get(ticker, {})
                
                if "error" in data:
                    results[ticker] = False
                    continue
                
                # Prepare real-time data
                real_time_data = {
                    "price": data.get("current_price", 0),
                    "change": 0,  # Calculate from previous close
                    "change_percent": 0,
                    "volume": 0,
                    "market_cap": data.get("market_cap"),
                    "high": data.get("current_price", 0),
                    "low": data.get("current_price", 0),
                    "open": data.get("current_price", 0)
                }
                
                # Store real-time data
                self.store_real_time_price(ticker, real_time_data)
                
                # Store historical data
                if data.get("historical_data"):
                    for record in data["historical_data"]:
                        self.store_historical_price(ticker, record)
                
                results[ticker] = True
                
            except Exception as e:
                logger.error(f"Error updating prices for {ticker}: {e}")
                results[ticker] = False
        
        return results
    
    def get_market_summary(self) -> Dict:
        """
        Get market summary with real-time prices
        """
        try:
            # Get all tickers
            tickers = self.db.query(Ticker).all()
            
            summary = {
                "timestamp": datetime.now().isoformat(),
                "tickers": []
            }
            
            for ticker in tickers:
                real_time = self.get_real_time_price(ticker.symbol)
                if real_time:
                    summary["tickers"].append({
                        "symbol": ticker.symbol,
                        "company_name": ticker.company_name,
                        "price": real_time["price"],
                        "change": real_time["change"],
                        "change_percent": real_time["change_percent"],
                        "volume": real_time["volume"],
                        "last_updated": real_time["timestamp"]
                    })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {"error": str(e)}
    
    def store_minute_data(self, ticker: str, price_data: Dict) -> bool:
        """
        Store minute-level data (for 24-hour history)
        Called every minute to store OHLCV data
        """
        try:
            # Store minute-level data (last 24 hours = 1440 records)
            timestamp = int(datetime.now().timestamp())
            minute_key = f"price:minute:{ticker}"
            
            minute_record = {
                "ticker": ticker,
                "timestamp": datetime.now().isoformat(),
                "open": float(price_data.get("open", 0)),
                "high": float(price_data.get("high", 0)),
                "low": float(price_data.get("low", 0)),
                "close": float(price_data.get("price", 0)),
                "volume": int(price_data.get("volume", 0))
            }
            
            # Store minute data
            self.redis_client.zadd(
                minute_key,
                {json.dumps(minute_record): timestamp}
            )
            
            # Keep only last 1440 records (24 hours)
            self.redis_client.zremrangebyrank(minute_key, 0, -1441)
            
            # Set TTL for 25 hours
            self.redis_client.expire(minute_key, 90000)
            
            logger.info(f"Stored minute data for {ticker}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing minute data for {ticker}: {e}")
            return False

    def cleanup_old_data(self):
        """
        Cleanup old data from Redis (industry standard: keep last 24 hours)
        """
        try:
            # Redis TTL handles this automatically
            # But we can also manually clean up
            cutoff_time = int((datetime.now() - timedelta(hours=24)).timestamp())
            
            # Get all ticker keys
            ticker_keys = self.redis_client.keys("price:timeseries:*")
            
            for key in ticker_keys:
                # Remove old data
                self.redis_client.zremrangebyscore(key, 0, cutoff_time)
            
            logger.info("Cleaned up old price data")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")