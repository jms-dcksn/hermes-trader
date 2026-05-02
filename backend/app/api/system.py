from fastapi import APIRouter
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """Health check endpoint for Docker/deployment."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "FinAlly AI Trading Workstation"
    }