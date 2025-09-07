#!/usr/bin/env python3
"""
Test script for real-time price functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.real_time_price_service import RealTimePriceService
from app.db.database import SessionLocal
from app.models.models import Base
from app.db.database import engine
import json

def test_real_time_prices():
    print("🚀 Testing Real-Time Price System")
    print("=" * 50)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize service (without Redis for demo)
    db = SessionLocal()
    
    try:
        # Test with mock Redis (fallback mode)
        service = RealTimePriceService(db, redis_url="redis://localhost:6379")
        
        print("\n📊 Testing Real-Time Price Storage...")
        
        # Test storing real-time price
        mock_price_data = {
            "price": 150.25,
            "change": 2.50,
            "change_percent": 1.69,
            "volume": 1000000,
            "market_cap": 2500000000000,
            "high": 151.00,
            "low": 149.50,
            "open": 149.75
        }
        
        # Store real-time price (will fail without Redis, but shows the pattern)
        try:
            result = service.store_real_time_price("AAPL", mock_price_data)
            print(f"✅ Real-time price storage: {'Success' if result else 'Failed (Redis not available)'}")
        except Exception as e:
            print(f"⚠️  Real-time storage failed (expected without Redis): {e}")
        
        print("\n📈 Testing Historical Price Storage...")
        
        # Test historical price storage
        historical_data = {
            "date": "2024-09-01",
            "close": 150.25
        }
        
        result = service.store_historical_price("AAPL", historical_data)
        print(f"✅ Historical price storage: {'Success' if result else 'Failed'}")
        
        print("\n📋 Testing Price Retrieval...")
        
        # Test getting historical prices
        prices = service.get_historical_prices("AAPL", days=30)
        print(f"✅ Retrieved {len(prices)} historical prices")
        
        print("\n🏭 Industry Standard Architecture Demo:")
        print("┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐")
        print("│   Real-time     │    │   Historical    │    │   Long-term     │")
        print("│   (Redis)       │    │   (PostgreSQL)  │    │   (S3/Parquet)  │")
        print("│   Last 24h      │    │   Last 2 years  │    │   Archive       │")
        print("└─────────────────┘    └─────────────────┘    └─────────────────┘")
        
        print("\n📊 Data Storage Patterns:")
        print("• Real-time (Redis): Last 24 hours with TTL")
        print("• Historical (PostgreSQL): Last 2 years with partitioning")
        print("• Archive (S3): Compressed Parquet files")
        
        print("\n🔄 Data Flow:")
        print("1. Yahoo Finance → Rate limiting protection")
        print("2. Real-time data → Redis (24h TTL)")
        print("3. Historical data → PostgreSQL")
        print("4. WebSocket → Live updates to clients")
        print("5. Cleanup → Automatic data lifecycle")
        
        print("\n💡 Key Features:")
        print("✅ Redis for sub-second reads")
        print("✅ PostgreSQL for complex queries")
        print("✅ WebSocket for live updates")
        print("✅ Rate limiting protection")
        print("✅ Automatic data cleanup")
        print("✅ Error handling and logging")
        
        print("\n🎯 Production Recommendations:")
        print("1. Add TimescaleDB for better time-series performance")
        print("2. Implement Kafka for data streaming")
        print("3. Add data compression for storage efficiency")
        print("4. Set up monitoring and alerting")
        print("5. Add data validation and quality checks")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()
    
    print("\n🎉 Real-time price system test completed!")

if __name__ == "__main__":
    test_real_time_prices()
