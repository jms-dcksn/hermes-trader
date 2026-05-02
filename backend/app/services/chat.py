import json
import logging
from typing import Dict, List, Optional, Any
import os
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM chat integration with structured outputs."""
    
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = "openrouter/openai/gpt-oss-120b"
        
        if not self.openrouter_api_key and not mock_mode:
            logger.warning("OPENROUTER_API_KEY not set. LLM will use mock mode.")
            self.mock_mode = True
    
    async def chat(
        self,
        user_message: str,
        portfolio_context: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Process chat message with LLM.
        
        Returns:
            Dict with keys: message, trades, watchlist_changes
        """
        if self.mock_mode:
            return self._mock_response(user_message, portfolio_context)
        
        try:
            return await self._call_openrouter(
                user_message, portfolio_context, conversation_history
            )
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            # Fall back to mock response
            return self._mock_response(user_message, portfolio_context)
    
    def _mock_response(
        self, 
        user_message: str, 
        portfolio_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a deterministic mock response for testing."""
        user_message_lower = user_message.lower()
        
        # Default response
        response = {
            "message": "I'm analyzing your portfolio now. In mock mode, I can't execute real trades.",
            "trades": [],
            "watchlist_changes": []
        }
        
        # Simple rule-based responses
        if "hello" in user_message_lower or "hi" in user_message_lower:
            response["message"] = "Hello! I'm FinAlly, your AI trading assistant. I can help you analyze your portfolio, suggest trades, and manage your watchlist."
        
        elif "portfolio" in user_message_lower:
            cash = portfolio_context.get("cash_balance", 0)
            total = portfolio_context.get("total_value", cash)
            positions = portfolio_context.get("positions", [])
            
            if positions:
                position_summary = ", ".join([f"{p['ticker']}: {p['quantity']} shares" for p in positions[:3]])
                if len(positions) > 3:
                    position_summary += f" and {len(positions) - 3} more positions"
                
                response["message"] = f"Your portfolio is worth ${total:,.2f} (cash: ${cash:,.2f}). You have {len(positions)} positions including {position_summary}."
            else:
                response["message"] = f"Your portfolio is worth ${total:,.2f} (all in cash). You have no positions yet."
        
        elif "buy" in user_message_lower and "aapl" in user_message_lower:
            response["message"] = "I'll execute a buy order for 10 shares of AAPL at the current market price."
            response["trades"] = [{"ticker": "AAPL", "side": "buy", "quantity": 10}]
        
        elif "sell" in user_message_lower and "googl" in user_message_lower:
            response["message"] = "I'll execute a sell order for 5 shares of GOOGL at the current market price."
            response["trades"] = [{"ticker": "GOOGL", "side": "sell", "quantity": 5}]
        
        elif "watchlist" in user_message_lower and "add" in user_message_lower:
            # Extract ticker (simple regex would be better)
            if "tsla" in user_message_lower:
                ticker = "TSLA"
            elif "amzn" in user_message_lower:
                ticker = "AMZN"
            else:
                ticker = "PYPL"  # default
            
            response["message"] = f"I'll add {ticker} to your watchlist."
            response["watchlist_changes"] = [{"ticker": ticker, "action": "add"}]
        
        return response
    
    async def _call_openrouter(
        self,
        user_message: str,
        portfolio_context: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Call OpenRouter via LiteLLM for structured output."""
        try:
            import litellm
        except ImportError:
            logger.error("LiteLLM not installed. Falling back to mock mode.")
            return self._mock_response(user_message, portfolio_context)
        
        # Construct system prompt
        system_prompt = self._build_system_prompt(portfolio_context)
        
        # Construct messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Structured output schema
        structured_schema = {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "trades": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ticker": {"type": "string"},
                            "side": {"type": "string", "enum": ["buy", "sell"]},
                            "quantity": {"type": "number"}
                        },
                        "required": ["ticker", "side", "quantity"]
                    }
                },
                "watchlist_changes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ticker": {"type": "string"},
                            "action": {"type": "string", "enum": ["add", "remove"]}
                        },
                        "required": ["ticker", "action"]
                    }
                }
            },
            "required": ["message"]
        }
        
        try:
            # Call LiteLLM with structured output
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                api_key=self.openrouter_api_key,
                response_format={"type": "json_object", "schema": structured_schema},
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Validate structure
            if "message" not in result:
                result["message"] = "I've processed your request."
            
            if "trades" not in result:
                result["trades"] = []
            
            if "watchlist_changes" not in result:
                result["watchlist_changes"] = []
            
            return result
            
        except Exception as e:
            logger.error(f"Error in LLM call: {e}")
            raise
    
    def _build_system_prompt(self, portfolio_context: Dict[str, Any]) -> str:
        """Build system prompt with portfolio context."""
        cash = portfolio_context.get("cash_balance", 0)
        total = portfolio_context.get("total_value", cash)
        positions = portfolio_context.get("positions", [])
        
        prompt = """You are FinAlly, an AI trading assistant. Your role is to help users manage their trading portfolio, analyze positions, suggest trades, and manage their watchlist.

You MUST respond with valid JSON matching this exact schema:
{
  "message": "Your conversational response to the user",
  "trades": [
    {"ticker": "AAPL", "side": "buy", "quantity": 10}
  ],
  "watchlist_changes": [
    {"ticker": "PYPL", "action": "add"}
  ]
}

Only include trades and watchlist_changes when the user explicitly asks for them or when you're making recommendations that should be auto-executed.

Current Portfolio Context:
"""
        prompt += f"- Cash balance: ${cash:,.2f}\n"
        prompt += f"- Total portfolio value: ${total:,.2f}\n"
        
        if positions:
            prompt += "- Current positions:\n"
            for pos in positions:
                pnl_sign = "+" if pos["unrealized_pnl"] >= 0 else ""
                prompt += f"  • {pos['ticker']}: {pos['quantity']} shares @ avg ${pos['avg_cost']:.2f}, current ${pos['current_price']:.2f} ({pnl_sign}{pos['unrealized_pnl_percent']:.2f}% P&L)\n"
        else:
            prompt += "- No positions currently held.\n"
        
        prompt += """
Guidelines:
1. Be concise and data-driven in your responses
2. Analyze portfolio composition, risk concentration, and P&L
3. Suggest trades with reasoning when appropriate
4. Execute trades when the user asks or agrees (auto-execute in this simulated environment)
5. Manage the watchlist proactively
6. Always respond with valid structured JSON
"""
        
        return prompt