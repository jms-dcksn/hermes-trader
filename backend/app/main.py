from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

from app.services.market_data import MarketSimulator
from app.services.streaming import MarketDataService, market_data_service
from app.services.portfolio import PortfolioService
from app.services.chat import LLMService
from app.core.database import DatabaseManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances
portfolio_service = None
chat_service = None
database_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("Starting FinAlly application...")
    
    # Initialize database
    global database_manager
    database_manager = DatabaseManager()
    database_manager.initialize_database()
    
    # Initialize market data service
    global market_data_service
    simulator = MarketSimulator()
    market_data_service = MarketDataService(simulator)
    await market_data_service.start()
    
    # Initialize other services
    global portfolio_service, chat_service
    portfolio_service = PortfolioService()
    
    # Check if we should use mock LLM mode
    llm_mock = os.getenv("LLM_MOCK", "false").lower() == "true"
    chat_service = LLMService(mock_mode=llm_mock)
    
    logger.info("FinAlly application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FinAlly application...")
    if market_data_service:
        await market_data_service.stop()
    logger.info("FinAlly application shutdown complete")

# Export accessor functions for routers
def get_market_data_service():
    """Get the market data service instance."""
    return market_data_service

def get_portfolio_service():
    """Get the portfolio service instance."""
    return portfolio_service

def get_chat_service():
    """Get the chat service instance."""
    return chat_service

# Create FastAPI app
app = FastAPI(
    title="FinAlly AI Trading Workstation",
    description="AI-powered trading workstation with live market data and LLM assistant",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware (though not strictly needed with static export)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.api import market_data, portfolio, watchlist, chat, system

# Include routers
app.include_router(market_data.router, prefix="/api", tags=["Market Data"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["Watchlist"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(system.router, prefix="/api", tags=["System"])

# Mount static files (will be populated after frontend build)
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

@app.get("/")
async def root():
    """Root endpoint - serves frontend."""
    if static_path.exists():
        index_path = static_path / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
    
    return HTMLResponse("""
    <html>
        <head><title>FinAlly - AI Trading Workstation</title></head>
        <body>
            <h1>FinAlly AI Trading Workstation</h1>
            <p>Backend is running. Frontend not built yet.</p>
            <p><a href="/docs">API Documentation</a></p>
        </body>
    </html>
    """)