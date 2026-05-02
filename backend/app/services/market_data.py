from abc import ABC, abstractmethod
from typing import Dict, Optional
import asyncio
from datetime import datetime
import numpy as np
import logging

logger = logging.getLogger(__name__)

class MarketDataProvider(ABC):
    """Abstract base class for market data providers."""
    
    @abstractmethod
    async def start(self):
        """Start the market data provider."""
        pass
    
    @abstractmethod
    async def stop(self):
        """Stop the market data provider."""
        pass
    
    @abstractmethod
    def get_price(self, ticker: str) -> Optional[float]:
        """Get current price for a ticker."""
        pass
    
    @abstractmethod
    def get_all_prices(self) -> Dict[str, float]:
        """Get current prices for all tickers."""
        pass


class MarketSimulator(MarketDataProvider):
    """Simulated market data using geometric Brownian motion."""
    
    def __init__(self, tickers: list = None):
        self.tickers = tickers or [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
            "NVDA", "META", "JPM", "V", "NFLX"
        ]
        
        # Starting prices (realistic approximations)
        self.start_prices = {
            "AAPL": 190.0, "GOOGL": 175.0, "MSFT": 420.0, "AMZN": 180.0,
            "TSLA": 240.0, "NVDA": 950.0, "META": 500.0, "JPM": 200.0,
            "V": 280.0, "NFLX": 650.0
        }
        
        # GBM parameters: drift (daily) and volatility (daily)
        self.drift = 0.0001  # ~2.5% annual
        self.volatility = 0.02  # ~30% annual
        
        # Correlation matrix for more realistic moves
        self.corr_matrix = self._create_correlation_matrix()
        
        # Current prices
        self.prices = {ticker: self.start_prices.get(ticker, 100.0) 
                      for ticker in self.tickers}
        self.previous_prices = self.prices.copy()
        
        # Task for background updates
        self._update_task = None
        self._running = False
        
    def _create_correlation_matrix(self):
        """Create a correlation matrix to simulate correlated moves."""
        n = len(self.tickers)
        base_corr = 0.7  # Base correlation between stocks
        corr = np.full((n, n), base_corr)
        np.fill_diagonal(corr, 1.0)
        
        # Tech stocks more correlated
        tech_indices = [self.tickers.index(t) for t in ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA", "META"] 
                       if t in self.tickers]
        for i in tech_indices:
            for j in tech_indices:
                if i != j:
                    corr[i][j] = 0.85
        
        return corr
    
    async def start(self):
        """Start the simulation background task."""
        if self._running:
            return
        
        self._running = True
        self._update_task = asyncio.create_task(self._update_loop())
        logger.info("Market simulator started")
    
    async def stop(self):
        """Stop the simulation background task."""
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        logger.info("Market simulator stopped")
    
    async def _update_loop(self):
        """Background loop that updates prices every ~500ms."""
        dt = 1.0 / 252.0 / 6.5  # One trading day (6.5 hours) in years
        sqrt_dt = np.sqrt(dt)
        
        n = len(self.tickers)
        chol = np.linalg.cholesky(self.corr_matrix)
        
        event_counter = 0
        
        while self._running:
            try:
                # Generate correlated random shocks
                z = np.random.randn(n)
                correlated_shocks = chol @ z
                
                # Update each ticker
                for i, ticker in enumerate(self.tickers):
                    self.previous_prices[ticker] = self.prices[ticker]
                    
                    # GBM formula: S_t = S_{t-1} * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z)
                    mu = self.drift
                    sigma = self.volatility
                    
                    # Add occasional random events (5% chance each iteration)
                    event_shock = 0.0
                    if np.random.rand() < 0.05:
                        event_counter += 1
                        # Sudden move between -5% and +5%
                        event_shock = (np.random.rand() - 0.5) * 0.1
                        logger.debug(f"Event on {ticker}: {event_shock:.2%}")
                    
                    price_change = np.exp(
                        (mu - 0.5 * sigma**2) * dt + 
                        sigma * sqrt_dt * correlated_shocks[i] + 
                        event_shock
                    )
                    
                    self.prices[ticker] = max(0.01, self.prices[ticker] * price_change)
                
                await asyncio.sleep(0.5)  # Update every ~500ms
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in market simulator: {e}")
                await asyncio.sleep(1)
    
    def get_price(self, ticker: str) -> Optional[float]:
        """Get current price for a ticker."""
        return self.prices.get(ticker)
    
    def get_all_prices(self) -> Dict[str, float]:
        """Get current prices for all tickers."""
        return self.prices.copy()
    
    def get_price_with_change(self, ticker: str) -> Dict[str, any]:
        """Get price with change information."""
        current = self.prices.get(ticker)
        previous = self.previous_prices.get(ticker)
        
        if current is None or previous is None:
            return None
        
        change = current - previous
        change_pct = (change / previous * 100) if previous != 0 else 0
        
        return {
            "ticker": ticker,
            "price": current,
            "previous_price": previous,
            "change": change,
            "change_percent": change_pct,
            "direction": "up" if change > 0 else "down" if change < 0 else "same",
            "timestamp": datetime.now().isoformat()
        }