from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import json
import logging
from app.services.streaming import market_data_service

router = APIRouter()
logger = logging.getLogger(__name__)

async def price_event_generator():
    """Generate Server-Sent Events for price updates."""
    try:
        async with market_data_service.sse_connection() as queue:
            # Send initial prices
            all_prices = market_data_service.price_cache.get_all_price_data()
            for price_data in all_prices:
                event_data = json.dumps(price_data)
                yield f"data: {event_data}\n\n"
            
            # Keep connection open and stream updates
            while True:
                message = await queue.get()
                yield message
                
    except asyncio.CancelledError:
        logger.info("SSE connection closed by client")
    except Exception as e:
        logger.error(f"Error in SSE stream: {e}")
        raise

@router.get("/stream/prices")
async def stream_prices():
    """SSE endpoint for real-time price updates."""
    return StreamingResponse(
        price_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )