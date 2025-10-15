"""
TradeStation integration module for chatbot and application systems.

This module provides integration between the TradeStation API and chatbot applications,
allowing users to query real-time market data and trading information through
natural language interactions.
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, skip loading
    pass

try:
    from .tradestation_api import TradeStationAPI, create_tradestation_client
except ImportError:
    # Fallback for when running as standalone script
    from tradestation_api import TradeStationAPI, create_tradestation_client

logger = logging.getLogger(__name__)


class TradeStationIntegration:
    """
    Integration class for TradeStation API with chatbot and application systems.
    
    Provides methods to interpret user queries and fetch relevant market data
    or trading information from TradeStation API.
    """
    
    def __init__(self, api_client: Optional[TradeStationAPI] = None):
        """
        Initialize TradeStation integration.
        
        Args:
            api_client: Optional TradeStation API client (creates one if not provided)
        """
        self.api_client = api_client or self._create_client()
        self.is_authenticated = True  # Always authenticated with refresh token approach
        
        logger.info("TradeStation integration initialized")
    
    def _create_client(self) -> TradeStationAPI:
        """Create TradeStation API client from configuration."""
        try:
            return create_tradestation_client()
        except Exception as e:
            logger.error(f"Failed to create TradeStation client: {e}")
            raise
    
    
    def is_connected(self) -> bool:
        """Check if connected to TradeStation API."""
        return self.api_client.access_token is not None
    
    # Market Data Query Methods
    
    def get_quote_for_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        Get quote data for a symbol and format for application response.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Formatted quote data for application display
        """
        try:
            if not self.is_connected():
                return {
                    "error": "Not connected to TradeStation API. Please authenticate first.",
                    "success": False
                }
            
            quote_data = self.api_client.get_quote(symbol.upper())
            
            if not quote_data:
                return {
                    "error": f"Could not retrieve quote for {symbol}",
                    "success": False
                }
            
            # Format quote data for display
            formatted_data = self._format_quote_data(quote_data, symbol)
            return {
                "data": formatted_data,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return {
                "error": f"Error retrieving quote: {str(e)}",
                "success": False
            }
    
    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Get quotes for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Formatted quotes data for application display
        """
        try:
            if not self.is_connected():
                return {
                    "error": "Not connected to TradeStation API. Please authenticate first.",
                    "success": False
                }
            
            quotes_data = self.api_client.get_quotes([s.upper() for s in symbols])
            
            if not quotes_data:
                return {
                    "error": f"Could not retrieve quotes for symbols: {', '.join(symbols)}",
                    "success": False
                }
            
            formatted_quotes = {}
            for symbol in symbols:
                if symbol.upper() in quotes_data:
                    formatted_quotes[symbol] = self._format_quote_data(
                        quotes_data[symbol.upper()], symbol
                    )
            
            return {
                "data": formatted_quotes,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting multiple quotes: {e}")
            return {
                "error": f"Error retrieving quotes: {str(e)}",
                "success": False
            }
    
    def get_historical_data(
        self, 
        symbol: str, 
        interval: str = "1Day",
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get historical data for a symbol.
        
        Args:
            symbol: Stock symbol
            interval: Data interval (1Min, 5Min, 1Hour, 1Day, etc.)
            days_back: Number of days to look back
            
        Returns:
            Formatted historical data
        """
        try:
            if not self.is_connected():
                return {
                    "error": "Not connected to TradeStation API. Please authenticate first.",
                    "success": False
                }
            
            # Calculate start date
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")
            
            hist_data = self.api_client.get_historical_data(
                symbol=symbol.upper(),
                interval=1,
                unit="Daily",
                start_date=start_date
            )
            
            if not hist_data:
                return {
                    "error": f"Could not retrieve historical data for {symbol}",
                    "success": False
                }
            
            formatted_data = self._format_historical_data(hist_data, symbol, interval)
            return {
                "data": formatted_data,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return {
                "error": f"Error retrieving historical data: {str(e)}",
                "success": False
            }
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status."""
        try:
            if not self.is_connected():
                return {
                    "error": "Not connected to TradeStation API. Please authenticate first.",
                    "success": False
                }
            
            status_data = self.api_client.get_market_status()
            
            if not status_data:
                return {
                    "error": "Could not retrieve market status",
                    "success": False
                }
            
            return {
                "data": status_data,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return {
                "error": f"Error retrieving market status: {str(e)}",
                "success": False
            }
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        try:
            if not self.is_connected():
                return {
                    "error": "Not connected to TradeStation API. Please authenticate first.",
                    "success": False
                }
            
            accounts = self.api_client.get_accounts()
            
            if not accounts:
                return {
                    "error": "Could not retrieve account information",
                    "success": False
                }
            
            # Get details for first account (typically main account)
            if accounts:
                account_id = accounts[0].get('Key')
                if account_id:
                    balance_data = self.api_client.get_account_balance(account_id)
                    positions = self.api_client.get_positions(account_id)
                    
                    return {
                        "data": {
                            "accounts": accounts,
                            "balance": balance_data,
                            "positions": positions
                        },
                        "success": True,
                        "timestamp": datetime.now().isoformat()
                    }
            
            return {
                "data": {"accounts": accounts},
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {
                "error": f"Error retrieving account information: {str(e)}",
                "success": False
            }
    
    # Query Processing Methods
    
    def process_market_query(self, query: str) -> Dict[str, Any]:
        """
        Process a market-related query and return appropriate data.
        
        Args:
            query: User query about market data
            
        Returns:
            Market data response
        """
        query_lower = query.lower()
        
        # Extract symbols from query (simple pattern matching)
        symbols = self._extract_symbols_from_query(query)
        
        # Determine query type and process accordingly
        if "quote" in query_lower or "price" in query_lower:
            if symbols:
                if len(symbols) == 1:
                    return self.get_quote_for_symbol(symbols[0])
                else:
                    return self.get_multiple_quotes(symbols)
            else:
                return {
                    "error": "Please specify a stock symbol for quote information",
                    "success": False
                }
        
        elif "historical" in query_lower or "chart" in query_lower or "history" in query_lower:
            if symbols:
                return self.get_historical_data(symbols[0])
            else:
                return {
                    "error": "Please specify a stock symbol for historical data",
                    "success": False
                }
        
        elif "market status" in query_lower or "market open" in query_lower:
            return self.get_market_status()
        
        elif "account" in query_lower or "balance" in query_lower or "positions" in query_lower:
            return self.get_account_info()
        
        else:
            return {
                "error": "I can help you with quotes, historical data, market status, and account information. Please be more specific.",
                "success": False
            }
    
    # Helper Methods
    
    def _extract_symbols_from_query(self, query: str) -> List[str]:
        """
        Extract stock symbols from a query string.
        
        Args:
            query: User query string
            
        Returns:
            List of extracted symbols
        """
        import re
        
        # Simple pattern to match common stock symbols (3-5 uppercase letters)
        symbol_pattern = r'\b[A-Z]{3,5}\b'
        matches = re.findall(symbol_pattern, query.upper())
        
        # Filter out common words that might match the pattern
        common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'HAD', 'BUT', 'NOT', 'WHAT', 'ALL', 'WERE', 'WHEN', 'YOUR', 'SAID', 'EACH', 'WHICH', 'THEIR', 'TIME', 'WILL', 'ABOUT', 'IF', 'UP', 'OUT', 'MANY', 'THEN', 'THEM', 'THESE', 'SO', 'SOME', 'HER', 'WOULD', 'MAKE', 'LIKE', 'INTO', 'HIM', 'TWO', 'MORE', 'GO', 'NO', 'WAY', 'COULD', 'MY', 'THAN', 'FIRST', 'VERY', 'OVER', 'THINK', 'WHERE', 'MOST', 'PEOPLE', 'KNOW', 'JUST', 'INTO', 'TIME', 'HIM', 'TWO', 'MORE', 'GO', 'NO', 'WAY', 'COULD', 'MY', 'THAN', 'FIRST', 'VERY', 'OVER', 'THINK', 'WHERE', 'MOST', 'PEOPLE', 'KNOW', 'JUST'}
        
        symbols = [match for match in matches if match not in common_words]
        return symbols
    
    def _format_quote_data(self, quote_data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Format quote data for display."""
        try:
            # Extract relevant fields from TradeStation quote response
            formatted = {
                "symbol": symbol.upper(),
                "last_price": quote_data.get("LastPrice", "N/A"),
                "bid": quote_data.get("Bid", "N/A"),
                "ask": quote_data.get("Ask", "N/A"),
                "volume": quote_data.get("Volume", "N/A"),
                "change": quote_data.get("Change", "N/A"),
                "change_percent": quote_data.get("ChangePercent", "N/A"),
                "high": quote_data.get("High", "N/A"),
                "low": quote_data.get("Low", "N/A"),
                "open": quote_data.get("Open", "N/A"),
                "timestamp": quote_data.get("Timestamp", "N/A")
            }
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting quote data: {e}")
            return {"symbol": symbol, "error": "Error formatting quote data"}
    
    def _format_historical_data(self, hist_data: Dict[str, Any], symbol: str, interval: str) -> Dict[str, Any]:
        """Format historical data for display."""
        try:
            # Extract bars data from TradeStation response
            bars = hist_data.get("Bars", [])
            
            if not bars:
                return {
                    "symbol": symbol,
                    "interval": interval,
                    "bars": [],
                    "message": "No historical data available"
                }
            
            # Format bars data
            formatted_bars = []
            for bar in bars[-10:]:  # Show last 10 bars
                formatted_bars.append({
                    "datetime": bar.get("DateTime", "N/A"),
                    "open": bar.get("Open", "N/A"),
                    "high": bar.get("High", "N/A"),
                    "low": bar.get("Low", "N/A"),
                    "close": bar.get("Close", "N/A"),
                    "volume": bar.get("Volume", "N/A")
                })
            
            return {
                "symbol": symbol.upper(),
                "interval": interval,
                "total_bars": len(bars),
                "recent_bars": formatted_bars,
                "latest_price": bars[-1].get("Close", "N/A") if bars else "N/A"
            }
            
        except Exception as e:
            logger.error(f"Error formatting historical data: {e}")
            return {"symbol": symbol, "error": "Error formatting historical data"}


def create_tradestation_integration() -> TradeStationIntegration:
    """
    Create a TradeStation integration instance.
    
    Returns:
        TradeStationIntegration instance
        
    Raises:
        ValueError: If TradeStation configuration is missing
    """
    try:
        return TradeStationIntegration()
    except Exception as e:
        raise ValueError(
            f"TradeStation API credentials not configured. "
            f"Set TRADESTATION_CLIENT_ID and TRADESTATION_CLIENT_SECRET environment variables. "
            f"Error: {e}"
        )


# Example usage
if __name__ == "__main__":
    import sys
    sys.path.insert(0, "..")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create integration
        ts_integration = create_tradestation_integration()
        
        print("✅ TradeStation integration created successfully!")
        print(f"📋 To use the integration:")
        print(f"   1. Get authorization URL: ts_integration.get_auth_url()")
        print(f"   2. Authenticate: ts_integration.authenticate(auth_code)")
        print(f"   3. Query market data: ts_integration.process_market_query('AAPL quote')")
        
    except Exception as e:
        print(f"❌ Error creating TradeStation integration: {e}")
