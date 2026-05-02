from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, DateTime, UniqueConstraint, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()
metadata = MetaData()

def generate_uuid():
    return str(uuid.uuid4())

class UserProfile(Base):
    __tablename__ = "users_profile"
    
    id = Column(String, primary_key=True, default="default")
    cash_balance = Column(Float, default=10000.0)
    created_at = Column(DateTime, server_default=func.now())


class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, default="default")
    ticker = Column(String, nullable=False)
    added_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (UniqueConstraint('user_id', 'ticker', name='uq_user_ticker'),)


class Position(Base):
    __tablename__ = "positions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, default="default")
    ticker = Column(String, nullable=False)
    quantity = Column(Float, default=0.0)
    avg_cost = Column(Float, default=0.0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('user_id', 'ticker', name='uq_user_position'),)


class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, default="default")
    ticker = Column(String, nullable=False)
    side = Column(String, nullable=False)  # "buy" or "sell"
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    executed_at = Column(DateTime, server_default=func.now())


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, default="default")
    total_value = Column(Float, nullable=False)
    recorded_at = Column(DateTime, server_default=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, default="default")
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    actions = Column(Text, nullable=True)  # JSON string of trades/watchlist changes
    created_at = Column(DateTime, server_default=func.now())