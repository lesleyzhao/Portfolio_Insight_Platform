"""
Real-time price API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
import json
import asyncio
from datetime import datetime

from app.db.database import get_db
from app.services.real_time_price_service import RealTimePriceService

router = APIRouter(prefix="/prices", tags=["real-time-prices"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

@router.get("/realtime/{ticker}")
def get_real_time_price(ticker: str, db: Session = Depends(get_db)):
    """Get latest real-time price for a ticker"""
    try:
        service = RealTimePriceService(db)
        price_data = service.get_real_time_price(ticker)
        
        if not price_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No real-time data found for {ticker}"
            )
        
        return {
            "ticker": ticker,
            "data": price_data,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting real-time price: {str(e)}"
        )

@router.get("/history/{ticker}")
def get_price_history(
    ticker: str, 
    hours: int = 24, 
    db: Session = Depends(get_db)
):
    """Get price history for a ticker (last N hours from Redis)"""
    try:
        service = RealTimePriceService(db)
        history = service.get_price_history(ticker, hours)
        
        return {
            "ticker": ticker,
            "hours": hours,
            "data_points": len(history),
            "history": history
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting price history: {str(e)}"
        )

@router.get("/historical/{ticker}")
def get_historical_prices(
    ticker: str, 
    days: int = 30, 
    db: Session = Depends(get_db)
):
    """Get historical prices from PostgreSQL"""
    try:
        service = RealTimePriceService(db)
        prices = service.get_historical_prices(ticker, days)
        
        return {
            "ticker": ticker,
            "days": days,
            "data_points": len(prices),
            "prices": prices
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting historical prices: {str(e)}"
        )

@router.post("/update")
def update_prices(
    tickers: List[str],
    db: Session = Depends(get_db)
):
    """Update real-time prices for given tickers"""
    try:
        service = RealTimePriceService(db)
        results = service.update_prices_from_yahoo(tickers)
        
        successful = sum(1 for success in results.values() if success)
        failed = len(results) - successful
        
        return {
            "message": f"Updated prices for {successful} tickers, {failed} failed",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating prices: {str(e)}"
        )

@router.get("/market-summary")
def get_market_summary(db: Session = Depends(get_db)):
    """Get market summary with all real-time prices"""
    try:
        service = RealTimePriceService(db)
        summary = service.get_market_summary()
        
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting market summary: {str(e)}"
        )

@router.websocket("/ws/{ticker}")
async def websocket_endpoint(websocket: WebSocket, ticker: str):
    """WebSocket endpoint for real-time price updates"""
    await manager.connect(websocket)
    try:
        service = RealTimePriceService(next(get_db()))
        
        while True:
            # Get latest price data
            price_data = service.get_real_time_price(ticker)
            
            if price_data:
                await manager.send_personal_message(
                    json.dumps({
                        "type": "price_update",
                        "ticker": ticker,
                        "data": price_data,
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
            
            # Wait 1 second before next update
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/cleanup")
def cleanup_old_data(db: Session = Depends(get_db)):
    """Cleanup old price data (industry standard maintenance)"""
    try:
        service = RealTimePriceService(db)
        service.cleanup_old_data()
        
        return {
            "message": "Old price data cleaned up successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cleaning up data: {str(e)}"
        )
