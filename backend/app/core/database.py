import sqlite3
from pathlib import Path
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "db/finally.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def initialize_database(self):
        """Create tables and seed default data if database is empty."""
        if not self.db_path.exists():
            logger.info("Database file not found, creating new database.")
        
        with self.get_connection() as conn:
            # Check if tables exist
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            if not tables:
                logger.info("No tables found, creating schema.")
                self.create_schema(conn)
                self.seed_data(conn)
    
    def create_schema(self, conn: sqlite3.Connection):
        """Create all database tables."""
        # Go up one level (core) then to models
        schema_path = Path(__file__).parent.parent / "models" / "schema.sql"
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        
        conn.executescript(schema_sql)
        conn.commit()
    
    def seed_data(self, conn: sqlite3.Connection):
        """Insert default seed data."""
        cursor = conn.cursor()
        
        # Insert default user
        cursor.execute("""
            INSERT OR IGNORE INTO users_profile (id, cash_balance)
            VALUES ('default', 10000.0)
        """)
        
        # Insert default watchlist
        default_tickers = [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
            "NVDA", "META", "JPM", "V", "NFLX"
        ]
        
        for ticker in default_tickers:
            cursor.execute("""
                INSERT OR IGNORE INTO watchlist (user_id, ticker)
                VALUES ('default', ?)
            """, (ticker,))
        
        conn.commit()
        logger.info("Default seed data inserted.")