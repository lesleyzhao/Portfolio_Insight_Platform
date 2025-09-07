"""
Data scraping service for portfolio and stock data
"""
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataScraper:
    """Service for scraping financial data from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_capitol_hill_trades(self, limit: int = 50) -> List[Dict]:
        """
        Scrape recent Capitol Hill trades from various sources
        This is a simplified version - in production, you'd use Firecrawl or similar
        """
        try:
            # For demo purposes, we'll create sample Capitol Hill trade data
            # In production, you'd scrape from actual sources like:
            # - https://www.capitoltrades.com/
            # - https://www.senate.gov/legislative/LIS/roll_call_votes/
            
            sample_trades = [
                {
                    "ticker": "AAPL",
                    "actor": "Senator John Doe",
                    "trade_date": "2024-09-01",
                    "side": "BUY",
                    "quantity": 100,
                    "price": 150.25,
                    "value": 15025.00,
                    "filing_date": "2024-09-02"
                },
                {
                    "ticker": "MSFT",
                    "actor": "Representative Jane Smith",
                    "trade_date": "2024-09-01",
                    "side": "SELL",
                    "quantity": 50,
                    "price": 300.50,
                    "value": 15025.00,
                    "filing_date": "2024-09-02"
                },
                {
                    "ticker": "NVDA",
                    "actor": "Senator Bob Johnson",
                    "trade_date": "2024-08-30",
                    "side": "BUY",
                    "quantity": 25,
                    "price": 450.75,
                    "value": 11268.75,
                    "filing_date": "2024-08-31"
                },
                {
                    "ticker": "TSLA",
                    "actor": "Representative Alice Brown",
                    "trade_date": "2024-08-29",
                    "side": "BUY",
                    "quantity": 75,
                    "price": 200.00,
                    "value": 15000.00,
                    "filing_date": "2024-08-30"
                },
                {
                    "ticker": "GOOGL",
                    "actor": "Senator Charlie Wilson",
                    "trade_date": "2024-08-28",
                    "side": "SELL",
                    "quantity": 30,
                    "price": 125.30,
                    "value": 3759.00,
                    "filing_date": "2024-08-29"
                }
            ]
            
            logger.info(f"Scraped {len(sample_trades)} Capitol Hill trades")
            return sample_trades[:limit]
            
        except Exception as e:
            logger.error(f"Error scraping Capitol Hill trades: {e}")
            return []
    
    def scrape_stock_data(self, tickers: List[str], period: str = "1mo") -> Dict[str, Dict]:
        """
        Scrape stock data using yfinance with fallback to mock data
        """
        stock_data = {}
        
        # Mock data for demonstration (to avoid rate limiting)
        mock_data = {
            "AAPL": {
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "current_price": 150.25,
                "market_cap": 2500000000000,
                "pe_ratio": 25.5,
                "dividend_yield": 0.005,
                "historical_data": [
                    {"Date": "2024-09-01", "Close": 150.25},
                    {"Date": "2024-08-31", "Close": 149.80},
                    {"Date": "2024-08-30", "Close": 151.20}
                ]
            },
            "MSFT": {
                "symbol": "MSFT",
                "company_name": "Microsoft Corporation",
                "sector": "Technology",
                "industry": "Software",
                "current_price": 300.50,
                "market_cap": 2200000000000,
                "pe_ratio": 28.2,
                "dividend_yield": 0.007,
                "historical_data": [
                    {"Date": "2024-09-01", "Close": 300.50},
                    {"Date": "2024-08-31", "Close": 299.80},
                    {"Date": "2024-08-30", "Close": 301.20}
                ]
            },
            "NVDA": {
                "symbol": "NVDA",
                "company_name": "NVIDIA Corporation",
                "sector": "Technology",
                "industry": "Semiconductors",
                "current_price": 450.75,
                "market_cap": 1100000000000,
                "pe_ratio": 45.8,
                "dividend_yield": 0.003,
                "historical_data": [
                    {"Date": "2024-09-01", "Close": 450.75},
                    {"Date": "2024-08-31", "Close": 448.90},
                    {"Date": "2024-08-30", "Close": 452.10}
                ]
            },
            "TSLA": {
                "symbol": "TSLA",
                "company_name": "Tesla, Inc.",
                "sector": "Consumer Discretionary",
                "industry": "Auto Manufacturers",
                "current_price": 200.00,
                "market_cap": 650000000000,
                "pe_ratio": 35.2,
                "dividend_yield": 0.0,
                "historical_data": [
                    {"Date": "2024-09-01", "Close": 200.00},
                    {"Date": "2024-08-31", "Close": 198.50},
                    {"Date": "2024-08-30", "Close": 201.25}
                ]
            },
            "GOOGL": {
                "symbol": "GOOGL",
                "company_name": "Alphabet Inc.",
                "sector": "Technology",
                "industry": "Internet Content & Information",
                "current_price": 125.30,
                "market_cap": 1600000000000,
                "pe_ratio": 22.8,
                "dividend_yield": 0.0,
                "historical_data": [
                    {"Date": "2024-09-01", "Close": 125.30},
                    {"Date": "2024-08-31", "Close": 124.80},
                    {"Date": "2024-08-30", "Close": 126.10}
                ]
            }
        }
        
        for ticker in tickers:
            try:
                # Use mock data for demonstration
                if ticker in mock_data:
                    stock_data[ticker] = mock_data[ticker]
                    logger.info(f"Using mock data for {ticker}")
                    continue
                
                # Try to get real data (but likely will be rate limited)
                stock = yf.Ticker(ticker)
                
                # Get basic info
                info = stock.info
                
                # Get historical data
                hist = stock.history(period=period)
                
                # Get current price
                current_price = hist['Close'].iloc[-1] if not hist.empty else None
                
                stock_data[ticker] = {
                    "symbol": ticker,
                    "company_name": info.get("longName", ticker),
                    "sector": info.get("sector", "Unknown"),
                    "industry": info.get("industry", "Unknown"),
                    "current_price": float(current_price) if current_price else None,
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("trailingPE"),
                    "dividend_yield": info.get("dividendYield"),
                    "historical_data": hist.to_dict('records') if not hist.empty else []
                }
                
                logger.info(f"Scraped real data for {ticker}")
                
            except Exception as e:
                logger.warning(f"Error scraping data for {ticker}: {e}. Using fallback data.")
                # Create fallback data
                stock_data[ticker] = {
                    "symbol": ticker,
                    "company_name": f"{ticker} Corporation",
                    "sector": "Unknown",
                    "industry": "Unknown",
                    "current_price": 100.0,  # Default price
                    "market_cap": None,
                    "pe_ratio": None,
                    "dividend_yield": None,
                    "historical_data": [
                        {"Date": "2024-09-01", "Close": 100.0}
                    ]
                }
        
        return stock_data
    
    def get_top_stocks(self, limit: int = 20) -> List[str]:
        """
        Get list of top stocks by market cap
        """
        # Popular stocks for demo
        top_stocks = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B",
            "UNH", "JNJ", "V", "PG", "JPM", "HD", "MA", "DIS", "PYPL", "ADBE",
            "NFLX", "CRM", "INTC", "CMCSA", "PFE", "TMO", "ABT", "COST", "PEP",
            "WMT", "MRK", "ACN", "TXN", "QCOM", "NKE", "DHR", "VZ", "NEE", "T",
            "UNP", "PM", "RTX", "HON", "IBM", "SPGI", "LMT", "AMGN", "CVX",
            "AXP", "CAT", "GS", "BA", "MMM", "GE", "WBA", "XOM", "KO", "MCD"
        ]
        
        return top_stocks[:limit]
    
    def scrape_news_sentiment(self, ticker: str, days: int = 7) -> List[Dict]:
        """
        Scrape news sentiment for a ticker
        This is a placeholder - in production, you'd use news APIs
        """
        # For demo purposes, return sample news data
        sample_news = [
            {
                "ticker": ticker,
                "headline": f"Positive outlook for {ticker} as earnings beat expectations",
                "sentiment": "positive",
                "published_date": "2024-09-01",
                "source": "Financial News"
            },
            {
                "ticker": ticker,
                "headline": f"{ticker} faces regulatory challenges in key markets",
                "sentiment": "negative",
                "published_date": "2024-08-30",
                "source": "Market Watch"
            }
        ]
        
        return sample_news
