from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class Trade(BaseModel):
    ticker: str
    side: str  # "buy" or "sell"
    quantity: float


class WatchlistChange(BaseModel):
    ticker: str
    action: str  # "add" or "remove"


class ChatResponse(BaseModel):
    message: str
    trades: Optional[List[Trade]] = None
    watchlist_changes: Optional[List[WatchlistChange]] = None


class Portfolio(BaseModel):
    cash_balance: float
    positions: List[dict]
    total_value: float
    unrealized_pnl: float


class PriceUpdate(BaseModel):
    ticker: str
    price: float
    previous_price: Optional[float] = None
    timestamp: datetime
    change: Optional[float] = None
    direction: Optional[str] = None  # "up", "down", "same"