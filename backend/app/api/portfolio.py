from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
import logging
from app.services.portfolio import PortfolioService
from app.main import get_market_data_service
from app.models.schemas import Trade

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependency
def get_portfolio_service():
    return PortfolioService()

@router.get("")
async def get_portfolio(
    service: PortfolioService = Depends(get_portfolio_service),
    user_id: str = "default"
):
    """Get current portfolio summary."""
    try:
        portfolio = service.get_portfolio(user_id)
        
        # Get the market data service from the app state
        md_service = get_market_data_service()
        if not md_service or not md_service.price_cache:
            raise HTTPException(status_code=503, detail="Market data service not ready")
        
        # Enhance with current prices from market data
        for position in portfolio["positions"]:
            ticker = position["ticker"]
            price_data = md_service.price_cache.get_price_data(ticker)
            if price_data:
                position["current_price"] = price_data["price"]
                position["change_percent"] = price_data["change_percent"]
                position["direction"] = price_data["direction"]
                
                # Recalculate P&L with actual current price
                quantity = position["quantity"]
                avg_cost = position["avg_cost"]
                current_price = price_data["price"]
                
                position["position_value"] = quantity * current_price
                position["unrealized_pnl"] = (current_price - avg_cost) * quantity
                position["unrealized_pnl_percent"] = ((current_price - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0
        
        # Recalculate total value with updated prices
        total_value = portfolio["cash_balance"]
        for position in portfolio["positions"]:
            total_value += position.get("position_value", 0)
        
        portfolio["total_value"] = total_value
        
        return portfolio
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trade")
async def execute_trade(
    trade: Trade,
    service: PortfolioService = Depends(get_portfolio_service),
    user_id: str = "default"
):
    """Execute a trade (buy or sell)."""
    try:
        # Get the market data service from the app state
        md_service = get_market_data_service()
        if not md_service or not md_service.price_cache:
            raise HTTPException(status_code=503, detail="Market data service not ready")
        
        # Get current price from market data
        price_data = md_service.price_cache.get_price_data(trade.ticker)
        if not price_data:
            raise HTTPException(status_code=400, detail=f"No price data for {trade.ticker}")
        
        current_price = price_data["price"]
        
        # Execute trade
        success, message = service.execute_trade(
            user_id, trade.ticker, trade.side, trade.quantity, current_price
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Record portfolio snapshot
        portfolio = service.get_portfolio(user_id)
        
        return {
            "success": True,
            "message": message,
            "price": current_price,
            "total_cost": trade.quantity * current_price,
            "portfolio": portfolio
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_portfolio_history(
    service: PortfolioService = Depends(get_portfolio_service),
    user_id: str = "default",
    limit: int = 100
):
    """Get portfolio value history for P&L chart."""
    try:
        history = service.get_portfolio_history(user_id, limit)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error getting portfolio history: {e}")
        raise HTTPException(status_code=500, detail=str(e))