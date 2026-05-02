import asyncio
from typing import Dict, List, Set
import json
from datetime import datetime
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class PriceCache:
    """In-memory cache for current prices."""
    
    def __init__(self):
        self.prices: Dict[str, float] = {}
        self.previous_prices: Dict[str, float] = {}
        self.timestamps: Dict[str, datetime] = {}
    
    def update(self, ticker: str, price: float):
        """Update price for a ticker."""
        if ticker in self.prices:
            self.previous_prices[ticker] = self.prices[ticker]
        
        self.prices[ticker] = price
        self.timestamps[ticker] = datetime.now()
    
    def update_all(self, prices: Dict[str, float]):
        """Update prices for multiple tickers."""
        for ticker, price in prices.items():
            self.update(ticker, price)
    
    def get_price_data(self, ticker: str) -> Dict[str, any]:
        """Get price with change information."""
        if ticker not in self.prices:
            return None
        
        current = self.prices[ticker]
        previous = self.previous_prices.get(ticker, current)
        
        change = current - previous
        change_pct = (change / previous * 100) if previous != 0 else 0
        
        return {
            "ticker": ticker,
            "price": current,
            "previous_price": previous,
            "change": change,
            "change_percent": change_pct,
            "direction": "up" if change > 0 else "down" if change < 0 else "same",
            "timestamp": self.timestamps[ticker].isoformat()
        }
    
    def get_all_price_data(self) -> List[Dict[str, any]]:
        """Get price data for all tickers."""
        return [
            self.get_price_data(ticker)
            for ticker in self.prices.keys()
            if self.get_price_data(ticker) is not None
        ]


class SSEManager:
    """Manage SSE connections for real-time price updates."""
    
    def __init__(self):
        self.connections: Set[asyncio.Queue] = set()
        self._task = None
    
    async def add_connection(self, queue: asyncio.Queue):
        """Add a new SSE connection."""
        self.connections.add(queue)
        logger.debug(f"New SSE connection added, total: {len(self.connections)}")
    
    async def remove_connection(self, queue: asyncio.Queue):
        """Remove an SSE connection."""
        self.connections.remove(queue)
        logger.debug(f"SSE connection removed, total: {len(self.connections)}")
    
    async def broadcast_price_update(self, price_data: Dict[str, any]):
        """Broadcast price update to all connected clients."""
        if not self.connections:
            return
        
        event_data = json.dumps(price_data)
        message = f"data: {event_data}\n\n"
        
        tasks = []
        for queue in self.connections.copy():  # Copy to avoid modification during iteration
            try:
                await queue.put(message)
            except Exception as e:
                logger.warning(f"Failed to send to SSE connection: {e}")
                # Connection might be stale, remove it
                self.connections.discard(queue)
    
    async def broadcast_all_prices(self, price_cache: PriceCache):
        """Broadcast all current prices."""
        all_prices = price_cache.get_all_price_data()
        for price_data in all_prices:
            await self.broadcast_price_update(price_data)


class MarketDataService:
    """Main service coordinating market data and SSE streaming."""
    
    def __init__(self, market_data_provider):
        self.provider = market_data_provider
        self.price_cache = PriceCache()
        self.sse_manager = SSEManager()
        self._running = False
        self._update_task = None
    
    async def start(self):
        """Start the market data service."""
        if self._running:
            return
        
        # Start the market data provider
        await self.provider.start()
        
        # Start the update loop
        self._running = True
        self._update_task = asyncio.create_task(self._update_loop())
        
        logger.info("Market data service started")
    
    async def stop(self):
        """Stop the market data service."""
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        
        await self.provider.stop()
        logger.info("Market data service stopped")
    
    async def _update_loop(self):
        """Background loop that reads from provider and updates cache/SSE."""
        while self._running:
            try:
                # Get latest prices from provider
                prices = self.provider.get_all_prices()
                
                # Update cache
                self.price_cache.update_all(prices)
                
                # Broadcast updates to SSE connections
                all_price_data = self.price_cache.get_all_price_data()
                for price_data in all_price_data:
                    await self.sse_manager.broadcast_price_update(price_data)
                
                # Wait before next update
                await asyncio.sleep(0.5)  # ~500ms updates
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in market data update loop: {e}")
                await asyncio.sleep(1)
    
    @asynccontextmanager
    async def sse_connection(self):
        """Context manager for SSE connections."""
        queue = asyncio.Queue()
        await self.sse_manager.add_connection(queue)
        
        try:
            yield queue
        finally:
            await self.sse_manager.remove_connection(queue)


# Global instance
market_data_service: MarketDataService = None