"""
TradeStation API integration module for real-time market data and trading operations.

This module provides a clean interface to TradeStation's REST API for:
- Market data retrieval
- Account information
- Order management
- Real-time quotes and charts
"""

from __future__ import annotations
import os
import logging
import requests
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, skip loading
    pass

logger = logging.getLogger(__name__)

@dataclass
class TradeStationConfig:
    """Configuration for TradeStation API client."""
    
    client_id: str
    client_secret: str
    refresh_token: Optional[str] = None
    base_url: str = "https://api.tradestation.com"
    sandbox_url: str = "https://sim-api.tradestation.com"
    use_sandbox: bool = False
    
    # API endpoints
    token_endpoint: str = "/oauth/token"
    user_endpoint: str = "/v3/users/me"
    accounts_endpoint: str = "/v3/accounts"
    marketdata_endpoint: str = "/v3/marketdata"
    orders_endpoint: str = "/v3/orders"
    
    # Authentication base URL
    auth_base_url: str = "https://signin.tradestation.com"
    
    def __post_init__(self) -> None:
        """Initialize API base URL based on environment."""
        if self.use_sandbox:
            self.base_url = self.sandbox_url


class TradeStationAPI:
    """
    TradeStation API client for market data and trading operations.
    
    Provides methods for authentication, market data retrieval, account management,
    and order operations.
    """
    
    def __init__(self, config: TradeStationConfig) -> None:
        """
        Initialize TradeStation API client.
        
        Args:
            config: TradeStation configuration object
        """
        self.config = config
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'TradeStation-API-Client/1.0'
        })
        
        logger.info(f"Initialized TradeStation API client (Sandbox: {config.use_sandbox})")
        
        # If refresh token is provided, try to get access token immediately
        if config.refresh_token:
            logger.info("Refresh token provided, attempting to get access token")
            if self.get_access_token_from_refresh():
                logger.info("Successfully obtained access token from refresh token")
            else:
                logger.warning("Failed to get access token from refresh token")
    
    def get_access_token_from_refresh(self) -> bool:
        """
        Get access token directly from refresh token.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.config.refresh_token:
            logger.error("No refresh token available")
            return False
            
        try:
            token_data = {
                'grant_type': 'refresh_token',
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret,
                'refresh_token': self.config.refresh_token
            }
            
            response = self.session.post(
                f"{self.config.auth_base_url}{self.config.token_endpoint}",
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                token_info = response.json()
                self.access_token = token_info.get('access_token')
                self.refresh_token = token_info.get('refresh_token', self.config.refresh_token)
                
                # Calculate token expiration
                expires_in = token_info.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                logger.info("Successfully obtained access token from refresh token")
                return True
            else:
                logger.error(f"Failed to get access token: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error getting access token from refresh token: {e}")
            return False
    
    
    def refresh_access_token(self) -> bool:
        """
        Refresh the access token using refresh token.
        
        Returns:
            True if refresh successful, False otherwise
        """
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False
            
        try:
            token_data = {
                'grant_type': 'refresh_token',
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret,
                'refresh_token': self.refresh_token
            }
            
            response = self.session.post(
                f"{self.config.auth_base_url}{self.config.token_endpoint}",
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                token_info = response.json()
                self.access_token = token_info.get('access_token')
                
                # Update refresh token if provided
                if 'refresh_token' in token_info:
                    self.refresh_token = token_info['refresh_token']
                
                # Calculate new expiration
                expires_in = token_info.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                logger.info("Successfully refreshed access token")
                return True
            else:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False
    
    def _ensure_authenticated(self) -> bool:
        """
        Ensure the client is authenticated and token is valid.
        
        Returns:
            True if authenticated, False otherwise
        """
        if not self.access_token:
            logger.error("Not authenticated - no access token")
            return False
        
        # Check if token is expired or about to expire (5 minute buffer)
        if self.token_expires_at and datetime.now() >= (self.token_expires_at - timedelta(minutes=5)):
            logger.info("Access token expired or about to expire, refreshing...")
            return self.refresh_access_token()
        
        return True
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Make authenticated API request to TradeStation.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data or None if request failed
        """
        if not self._ensure_authenticated():
            return None
        
        try:
            url = f"{self.config.base_url}{endpoint}"
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.warning("Unauthorized - attempting token refresh")
                if self.refresh_access_token():
                    # Retry request with new token
                    response = self.session.request(method, url, **kwargs)
                    if response.status_code == 200:
                        return response.json()
                logger.error("Authentication failed after refresh attempt")
                return None
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API request error: {e}")
            return None
    
    # Market Data Methods
    
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time quote for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
            
        Returns:
            Quote data or None if request failed
        """
        endpoint = f"{self.config.marketdata_endpoint}/quotes/{symbol}"
        return self._make_request('GET', endpoint)
    
    def get_quotes(self, symbols: List[str]) -> Optional[Dict[str, Any]]:
        """
        Get real-time quotes for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Quotes data or None if request failed
        """
        endpoint = f"{self.config.marketdata_endpoint}/quotes"
        params = {'symbols': ','.join(symbols)}
        return self._make_request('GET', endpoint, params=params)
    
    def get_historical_data(
        self, 
        symbol: str, 
        interval: int = 1,
        unit: str = "Daily", 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get historical price data for a symbol using TradeStation v3 API.
        
        Args:
            symbol: Stock symbol
            interval: Bar interval (1, 5, 15, 30, 60, etc.)
            unit: Time unit (Minute, Hour, Daily, Weekly, Monthly)
            start_date: Start date (YYYY-MM-DDTHH:MM:SSZ)
            end_date: End date (YYYY-MM-DDTHH:MM:SSZ)
            
        Returns:
            Historical data or None if request failed
        """
        endpoint = f"{self.config.marketdata_endpoint}/barcharts/{symbol}"
        params = {
            'interval': interval,
            'unit': unit
        }
        
        if start_date:
            params['startdate'] = start_date
        if end_date:
            params['enddate'] = end_date
            
        return self._make_request('GET', endpoint, params=params)
    
    def get_market_status(self) -> Optional[Dict[str, Any]]:
        """
        Get current market status.
        
        Returns:
            Market status data or None if request failed
        """
        endpoint = f"{self.config.marketdata_endpoint}/marketstatus"
        return self._make_request('GET', endpoint)
    
    # Account Methods
    
    def get_accounts(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get user's trading accounts.
        
        Returns:
            List of account information or None if request failed
        """
        endpoint = f"{self.config.accounts_endpoint}"
        response = self._make_request('GET', endpoint)
        return response.get('Accounts') if response else None
    
    def get_account_balance(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        Get account balance and positions.
        
        Args:
            account_id: Account identifier
            
        Returns:
            Account balance data or None if request failed
        """
        endpoint = f"{self.config.accounts_endpoint}/{account_id}/balances"
        return self._make_request('GET', endpoint)
    
    def get_positions(self, account_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get current positions for an account.
        
        Args:
            account_id: Account identifier
            
        Returns:
            List of positions or None if request failed
        """
        endpoint = f"{self.config.accounts_endpoint}/{account_id}/positions"
        response = self._make_request('GET', endpoint)
        return response.get('Positions') if response else None
    
    # Order Methods
    
    def get_orders(self, account_id: str, status: str = "All") -> Optional[List[Dict[str, Any]]]:
        """
        Get orders for an account.
        
        Args:
            account_id: Account identifier
            status: Order status filter (All, Open, Filled, Cancelled, etc.)
            
        Returns:
            List of orders or None if request failed
        """
        endpoint = f"{self.config.orders_endpoint}/{account_id}"
        params = {'status': status}
        response = self._make_request('GET', endpoint, params=params)
        return response.get('Orders') if response else None
    
    def place_order(
        self, 
        account_id: str, 
        symbol: str, 
        quantity: int, 
        order_type: str = "Market",
        side: str = "Buy",
        price: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Place a new order.
        
        Args:
            account_id: Account identifier
            symbol: Stock symbol
            quantity: Number of shares
            order_type: Order type (Market, Limit, Stop, etc.)
            side: Buy or Sell
            price: Price for limit orders
            
        Returns:
            Order confirmation or None if request failed
        """
        endpoint = f"{self.config.orders_endpoint}/{account_id}"
        
        order_data = {
            'Symbol': symbol,
            'Quantity': quantity,
            'OrderType': order_type,
            'TradeAction': side
        }
        
        if price and order_type == "Limit":
            order_data['Price'] = price
        
        return self._make_request('POST', endpoint, json=order_data)
    
    def cancel_order(self, account_id: str, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Cancel an existing order.
        
        Args:
            account_id: Account identifier
            order_id: Order identifier
            
        Returns:
            Cancellation confirmation or None if request failed
        """
        endpoint = f"{self.config.orders_endpoint}/{account_id}/{order_id}"
        return self._make_request('DELETE', endpoint)
    
    # Utility Methods
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Get user information.
        
        Returns:
            User information or None if request failed
        """
        endpoint = f"{self.config.user_endpoint}"
        return self._make_request('GET', endpoint)
    


def create_tradestation_client(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    refresh_token: Optional[str] = None,
    use_sandbox: bool = True
) -> TradeStationAPI:
    """
    Create a TradeStation API client with configuration from environment variables.
    
    Args:
        client_id: Optional client ID (defaults to TRADESTATION_CLIENT_ID env var)
        client_secret: Optional client secret (defaults to TRADESTATION_CLIENT_SECRET env var)
        refresh_token: Optional refresh token (defaults to TRADESTATION_CLIENT_REFRESH env var)
        use_sandbox: Whether to use sandbox environment
        
    Returns:
        Configured TradeStationAPI instance
        
    Raises:
        ValueError: If required configuration is missing
    """
    if client_id is None:
        client_id = os.getenv("TRADESTATION_CLIENT_ID")
    
    if client_secret is None:
        client_secret = os.getenv("TRADESTATION_CLIENT_SECRET")
    
    if refresh_token is None:
        refresh_token = os.getenv("TRADESTATION_CLIENT_REFRESH")
    
    if not client_id or not client_secret:
        raise ValueError(
            "TradeStation client ID and secret are required. "
            "Set TRADESTATION_CLIENT_ID and TRADESTATION_CLIENT_SECRET environment variables."
        )
    
    if not refresh_token:
        raise ValueError(
            "TradeStation refresh token is required. "
            "Set TRADESTATION_CLIENT_REFRESH environment variable."
        )
    
    config = TradeStationConfig(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        use_sandbox=use_sandbox
    )
    
    return TradeStationAPI(config)


# Example usage and testing functions
def test_tradestation_connection(api_client: TradeStationAPI) -> bool:
    """
    Test TradeStation API connection and basic functionality.
    
    Args:
        api_client: TradeStation API client
        
    Returns:
        True if test successful, False otherwise
    """
    try:
        # Test market status (doesn't require authentication)
        logger.info("Testing TradeStation API connection...")
        
        # Note: Most TradeStation endpoints require authentication
        # This is a basic connectivity test
        auth_url = api_client.get_auth_url()
        logger.info(f"Authorization URL generated: {auth_url}")
        
        logger.info("TradeStation API client initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"TradeStation API test failed: {e}")
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create client (will use environment variables)
        client = create_tradestation_client()
        
        # Test connection
        if test_tradestation_connection(client):
            print("✅ TradeStation API client setup successful!")
            print(f"📋 Next steps:")
            print(f"   1. Visit the authorization URL to get an authorization code")
            print(f"   2. Use client.authenticate(auth_code) to complete OAuth flow")
            print(f"   3. Start making API calls for market data and trading")
            
            # Show example barcharts API call
            print(f"\n📊 Example barcharts API call:")
            print(f"   GET {client.config.base_url}/v3/marketdata/barcharts/AAPL")
            print(f"   Parameters: interval=1&unit=Daily&startdate=2021-07-01T00:00:00Z&enddate=2025-07-15T23:59:59Z")
        else:
            print("❌ TradeStation API client setup failed!")
            
    except Exception as e:
        print(f"❌ Error setting up TradeStation API client: {e}")