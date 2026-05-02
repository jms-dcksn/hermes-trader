from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
import logging
from pydantic import BaseModel
from app.services.portfolio import PortfolioService
from app.services.streaming import market_data_service
from app.main import get_market_data_service

router = APIRouter()
logger = logging.getLogger(__name__)

class WatchlistAdd(BaseModel):
    ticker: str

# Dependency
def get_portfolio_service():
    return PortfolioService()

@router.get("")
async def get_watchlist(
    service: PortfolioService = Depends(get_portfolio_service),
    user_id: str = "default"
):
    """Get user's watchlist with latest prices."""
    try:
        tickers = service.get_watchlist(user_id)
        
        # Get the market data service from the app state
        md_service = get_market_data_service()
        if not md_service or not md_service.price_cache:
            raise HTTPException(status_code=503, detail="Market data service not ready")
        
        watchlist_data = []
        for ticker in tickers:
            price_data = md_service.price_cache.get_price_data(ticker)
            if price_data:
                watchlist_data.append({
                    "ticker": ticker,
                    "price": price_data["price"],
                    "change": price_data["change"],
                    "change_percent": price_data["change_percent"],
                    "direction": price_data["direction"],
                    "timestamp": price_data["timestamp"]
                })
            else:
                # Ticker not in cache yet (shouldn't happen for default watchlist)
                watchlist_data.append({
                    "ticker": ticker,
                    "price": None,
                    "change": None,
                    "change_percent": None,
                    "direction": None,
                    "timestamp": None
                })
        
        return {"watchlist": watchlist_data}
    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def add_to_watchlist(
    item: WatchlistAdd,
    service: PortfolioService = Depends(get_portfolio_service),
    user_id: str = "default"
):
    """Add a ticker to the watchlist."""
    try:
        ticker = item.ticker.upper().strip()
        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker cannot be empty")
        
        success = service.add_to_watchlist(user_id, ticker)
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Ticker {ticker} already in watchlist")
        
        return {"success": True, "message": f"Added {ticker} to watchlist"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{ticker}")
async def remove_from_watchlist(
    ticker: str,
    service: PortfolioService = Depends(get_portfolio_service),
    user_id: str = "default"
):
    """Remove a ticker from the watchlist."""
    try:
        ticker = ticker.upper().strip()
        success = service.remove_from_watchlist(user_id, ticker)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found in watchlist")
        
        return {"success": True, "message": f"Removed {ticker} from watchlist"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))