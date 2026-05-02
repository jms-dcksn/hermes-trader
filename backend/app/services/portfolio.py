import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class PortfolioService:
    """Service for portfolio management and trade execution."""
    
    def __init__(self, db_path: str = "db/finally.db"):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def get_portfolio(self, user_id: str = "default") -> Dict:
        """Get current portfolio summary."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get cash balance
            cursor.execute(
                "SELECT cash_balance FROM users_profile WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            cash_balance = row["cash_balance"] if row else 10000.0
            
            # Get positions
            cursor.execute(
                "SELECT ticker, quantity, avg_cost FROM positions WHERE user_id = ? AND quantity > 0",
                (user_id,)
            )
            positions = cursor.fetchall()
            
            # Calculate position values and P&L
            total_value = cash_balance
            positions_data = []
            
            for pos in positions:
                ticker = pos["ticker"]
                quantity = pos["quantity"]
                avg_cost = pos["avg_cost"]
                
                # Get current price (would come from market data service)
                # For now, we'll return avg_cost as placeholder
                current_price = avg_cost  # TODO: Get from market data service
                
                position_value = quantity * current_price
                unrealized_pnl = position_value - (quantity * avg_cost)
                unrealized_pnl_pct = (unrealized_pnl / (quantity * avg_cost) * 100) if quantity * avg_cost > 0 else 0
                
                positions_data.append({
                    "ticker": ticker,
                    "quantity": quantity,
                    "avg_cost": avg_cost,
                    "current_price": current_price,
                    "position_value": position_value,
                    "unrealized_pnl": unrealized_pnl,
                    "unrealized_pnl_percent": unrealized_pnl_pct
                })
                
                total_value += position_value
            
            # Calculate total unrealized P&L
            total_unrealized_pnl = sum(p["unrealized_pnl"] for p in positions_data)
            
            return {
                "cash_balance": cash_balance,
                "positions": positions_data,
                "total_value": total_value,
                "unrealized_pnl": total_unrealized_pnl
            }
    
    def execute_trade(self, user_id: str, ticker: str, side: str, quantity: float, price: float) -> Tuple[bool, str]:
        """Execute a trade (buy or sell)."""
        if side not in ["buy", "sell"]:
            return False, "Invalid side. Must be 'buy' or 'sell'"
        
        if quantity <= 0:
            return False, "Quantity must be positive"
        
        if price <= 0:
            return False, "Price must be positive"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get cash balance
            cursor.execute(
                "SELECT cash_balance FROM users_profile WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if not row:
                # Create user profile if it doesn't exist
                cursor.execute(
                    "INSERT INTO users_profile (id, cash_balance) VALUES (?, ?)",
                    (user_id, 10000.0)
                )
                cash_balance = 10000.0
            else:
                cash_balance = row["cash_balance"]
            
            if side == "buy":
                # Check sufficient cash
                cost = quantity * price
                if cost > cash_balance:
                    return False, f"Insufficient cash. Need ${cost:.2f}, have ${cash_balance:.2f}"
                
                # Update cash balance
                new_cash_balance = cash_balance - cost
                cursor.execute(
                    "UPDATE users_profile SET cash_balance = ? WHERE id = ?",
                    (new_cash_balance, user_id)
                )
                
                # Update or create position
                cursor.execute(
                    "SELECT quantity, avg_cost FROM positions WHERE user_id = ? AND ticker = ?",
                    (user_id, ticker)
                )
                row = cursor.fetchone()
                
                if row:
                    old_quantity = row["quantity"]
                    old_avg_cost = row["avg_cost"]
                    
                    new_quantity = old_quantity + quantity
                    new_avg_cost = ((old_quantity * old_avg_cost) + (quantity * price)) / new_quantity
                    
                    cursor.execute(
                        "UPDATE positions SET quantity = ?, avg_cost = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND ticker = ?",
                        (new_quantity, new_avg_cost, user_id, ticker)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO positions (user_id, ticker, quantity, avg_cost) VALUES (?, ?, ?, ?)",
                        (user_id, ticker, quantity, price)
                    )
            
            else:  # sell
                # Check sufficient shares
                cursor.execute(
                    "SELECT quantity, avg_cost FROM positions WHERE user_id = ? AND ticker = ?",
                    (user_id, ticker)
                )
                row = cursor.fetchone()
                
                if not row or row["quantity"] < quantity:
                    return False, f"Insufficient shares. Trying to sell {quantity}, have {row['quantity'] if row else 0}"
                
                old_quantity = row["quantity"]
                old_avg_cost = row["avg_cost"]
                
                # Update cash balance
                proceeds = quantity * price
                new_cash_balance = cash_balance + proceeds
                cursor.execute(
                    "UPDATE users_profile SET cash_balance = ? WHERE id = ?",
                    (new_cash_balance, user_id)
                )
                
                # Update position
                new_quantity = old_quantity - quantity
                if new_quantity > 0:
                    # Keep same avg_cost for remaining shares
                    cursor.execute(
                        "UPDATE positions SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND ticker = ?",
                        (new_quantity, user_id, ticker)
                    )
                else:
                    # Delete position if no shares left
                    cursor.execute(
                        "DELETE FROM positions WHERE user_id = ? AND ticker = ?",
                        (user_id, ticker)
                    )
            
            # Record trade
            cursor.execute(
                "INSERT INTO trades (user_id, ticker, side, quantity, price) VALUES (?, ?, ?, ?, ?)",
                (user_id, ticker, side, quantity, price)
            )
            
            # Record portfolio snapshot
            portfolio = self.get_portfolio(user_id)
            cursor.execute(
                "INSERT INTO portfolio_snapshots (user_id, total_value) VALUES (?, ?)",
                (user_id, portfolio["total_value"])
            )
            
            conn.commit()
            
            return True, "Trade executed successfully"
    
    def get_trade_history(self, user_id: str = "default", limit: int = 100) -> List[Dict]:
        """Get trade history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ticker, side, quantity, price, executed_at FROM trades WHERE user_id = ? ORDER BY executed_at DESC LIMIT ?",
                (user_id, limit)
            )
            
            trades = []
            for row in cursor.fetchall():
                trades.append({
                    "ticker": row["ticker"],
                    "side": row["side"],
                    "quantity": row["quantity"],
                    "price": row["price"],
                    "executed_at": row["executed_at"]
                })
            
            return trades
    
    def get_portfolio_history(self, user_id: str = "default", limit: int = 100) -> List[Dict]:
        """Get portfolio value history for P&L chart."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT total_value, recorded_at FROM portfolio_snapshots WHERE user_id = ? ORDER BY recorded_at DESC LIMIT ?",
                (user_id, limit)
            )
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "total_value": row["total_value"],
                    "recorded_at": row["recorded_at"]
                })
            
            return history
    
    def add_to_watchlist(self, user_id: str, ticker: str) -> bool:
        """Add ticker to watchlist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO watchlist (user_id, ticker) VALUES (?, ?)",
                    (user_id, ticker)
                )
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error:
                return False
    
    def remove_from_watchlist(self, user_id: str, ticker: str) -> bool:
        """Remove ticker from watchlist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM watchlist WHERE user_id = ? AND ticker = ?",
                (user_id, ticker)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_watchlist(self, user_id: str = "default") -> List[str]:
        """Get user's watchlist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ticker FROM watchlist WHERE user_id = ? ORDER BY added_at",
                (user_id,)
            )
            
            return [row["ticker"] for row in cursor.fetchall()]