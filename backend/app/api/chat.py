from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
import logging
from pydantic import BaseModel
from app.services.chat import LLMService
from app.services.portfolio import PortfolioService
from app.models.schemas import ChatResponse

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    message: str
    user_id: str = "default"

# Dependencies
def get_chat_service():
    llm_mock = False  # Will be set from env in main app
    return LLMService(mock_mode=llm_mock)

def get_portfolio_service():
    return PortfolioService()

@router.post("")
async def chat(
    chat_message: ChatMessage,
    chat_service: LLMService = Depends(get_chat_service),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """Send a message to the AI trading assistant."""
    try:
        user_id = chat_message.user_id
        
        # Get portfolio context
        portfolio_context = portfolio_service.get_portfolio(user_id)
        
        # Get conversation history (last 10 messages)
        # TODO: Implement conversation history retrieval from database
        conversation_history = []
        
        # Call LLM
        llm_response = await chat_service.chat(
            user_message=chat_message.message,
            portfolio_context=portfolio_context,
            conversation_history=conversation_history,
            user_id=user_id
        )
        
        # Execute trades from LLM response
        executed_trades = []
        if llm_response.get("trades"):
            for trade in llm_response["trades"]:
                try:
                    # Get current price
                    # Note: In production, we'd get this from market data service
                    # For now, we'll use portfolio service's execute_trade with a placeholder price
                    # The trade execution will fail if price is not available
                    
                    # We'll need market data service dependency here
                    # For now, skip actual execution in this example
                    logger.info(f"LLM requested trade: {trade}")
                    executed_trades.append({
                        "ticker": trade["ticker"],
                        "side": trade["side"],
                        "quantity": trade["quantity"],
                        "status": "pending_execution"
                    })
                except Exception as trade_error:
                    logger.error(f"Error executing trade {trade}: {trade_error}")
                    executed_trades.append({
                        "ticker": trade["ticker"],
                        "side": trade["side"],
                        "quantity": trade["quantity"],
                        "status": "failed",
                        "error": str(trade_error)
                    })
        
        # Execute watchlist changes
        executed_watchlist_changes = []
        if llm_response.get("watchlist_changes"):
            for change in llm_response["watchlist_changes"]:
                try:
                    if change["action"] == "add":
                        success = portfolio_service.add_to_watchlist(user_id, change["ticker"])
                    elif change["action"] == "remove":
                        success = portfolio_service.remove_from_watchlist(user_id, change["ticker"])
                    else:
                        continue
                    
                    executed_watchlist_changes.append({
                        "ticker": change["ticker"],
                        "action": change["action"],
                        "status": "success" if success else "failed"
                    })
                except Exception as change_error:
                    logger.error(f"Error executing watchlist change {change}: {change_error}")
                    executed_watchlist_changes.append({
                        "ticker": change["ticker"],
                        "action": change["action"],
                        "status": "failed",
                        "error": str(change_error)
                    })
        
        # TODO: Store chat message and actions in database
        
        return {
            "message": llm_response["message"],
            "trades": executed_trades,
            "watchlist_changes": executed_watchlist_changes,
            "timestamp": "2026-05-02T20:15:00Z"  # TODO: Use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))