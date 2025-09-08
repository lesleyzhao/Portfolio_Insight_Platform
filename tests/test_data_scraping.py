#!/usr/bin/env python3
"""
Test script for data scraping functionality
"""
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.data_scraper import DataScraper
from app.services.data_ingestion import DataIngestionService
from app.db.database import SessionLocal
from app.models.models import Base
from app.db.database import engine

def test_data_scraping():
    print("🧪 Testing Data Scraping Functionality")
    print("=" * 50)
    
    # Test data scraper
    scraper = DataScraper()
    
    # Test Capitol Hill trades
    print("\n📊 Testing Capitol Hill Trades Scraping...")
    trades = scraper.scrape_capitol_hill_trades(3)
    print(f"✅ Scraped {len(trades)} Capitol Hill trades")
    if trades:
        print(f"   Sample trade: {trades[0]['actor']} - {trades[0]['ticker']} {trades[0]['side']} {trades[0]['quantity']} @ ${trades[0]['price']}")
    
    # Test stock data scraping
    print("\n📈 Testing Stock Data Scraping...")
    stock_data = scraper.scrape_stock_data(['AAPL', 'MSFT', 'NVDA'])
    print(f"✅ Scraped data for {len(stock_data)} stocks")
    for symbol, data in stock_data.items():
        print(f"   {symbol}: {data['company_name']} - ${data['current_price']}")
    
    # Test data ingestion
    print("\n💾 Testing Data Ingestion...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Test ingesting tickers
    db = SessionLocal()
    service = DataIngestionService(db)
    
    tickers = service.ingest_tickers(['AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL'])
    print(f"✅ Ingested {len(tickers)} tickers into database")
    
    # Test creating sample portfolios
    portfolios = service.create_sample_portfolios('test-user-123')
    print(f"✅ Created {len(portfolios)} sample portfolios")
    
    # Show portfolio details
    for portfolio in portfolios:
        summary = service.get_portfolio_summary(portfolio.portfolio_id)
        if 'error' not in summary:
            print(f"   Portfolio: {summary['name']} - ${summary['total_value']:.2f} ({summary['holdings_count']} holdings)")
    
    db.close()
    
    print("\n🎉 All tests completed successfully!")
    print("\n📋 Summary:")
    print(f"   • Capitol Hill trades: {len(trades)}")
    print(f"   • Stock data scraped: {len(stock_data)}")
    print(f"   • Tickers ingested: {len(tickers)}")
    print(f"   • Portfolios created: {len(portfolios)}")

if __name__ == "__main__":
    test_data_scraping()
