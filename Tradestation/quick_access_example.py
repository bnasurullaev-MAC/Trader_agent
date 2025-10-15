#!/usr/bin/env python3
"""
Quick Access Example - Using Refresh Token to Get Access Token

This example shows how to use your refresh token to get an access token
and make API calls without going through the OAuth flow.
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Example of using refresh token for direct API access."""
    print("TradeStation Quick Access Example")
    print("=" * 50)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Check if refresh token is set
    refresh_token = os.getenv("TRADESTATION_CLIENT_REFRESH")
    
    if not refresh_token or refresh_token == "your-refresh-token-here":
        print("ERROR: Please set your refresh token in .env file:")
        print("TRADESTATION_CLIENT_REFRESH=your-actual-refresh-token")
        return
    
    try:
        from tradestation_api import create_tradestation_client
        
        print("Creating TradeStation client...")
        print("(This will automatically get access token from refresh token)")
        
        # Create client - it automatically gets access token from refresh token
        client = create_tradestation_client()
        
        if client.access_token:
            print(f"SUCCESS! Access token obtained: {client.access_token[:20]}...")
            
            print("\nNow you can make API calls directly!")
            
            # Example 1: Get market status
            print("\n1. Testing market status...")
            market_status = client.get_market_status()
            if market_status:
                print("Market status retrieved successfully!")
            else:
                print("Market status request failed")
            
            # Example 2: Get AAPL historical data (as you requested)
            print("\n2. Testing AAPL historical data...")
            hist_data = client.get_historical_data(
                symbol="AAPL",
                interval=1,
                unit="Daily",
                start_date="2021-07-01T00:00:00Z",
                end_date="2025-07-15T23:59:59Z"
            )
            
            if hist_data:
                print("Historical data retrieved successfully!")
                if 'Bars' in hist_data:
                    bars = hist_data['Bars']
                    print(f"Retrieved {len(bars)} data points")
                    if bars:
                        print(f"Date range: {bars[0].get('DateTime', 'N/A')} to {bars[-1].get('DateTime', 'N/A')}")
                        print(f"Latest price: ${bars[-1].get('Close', 'N/A')}")
            else:
                print("Historical data request failed")
            
            # Example 3: Get user info
            print("\n3. Testing user info...")
            user_info = client.get_user_info()
            if user_info:
                print("User info retrieved successfully!")
                print(f"User: {user_info.get('FirstName', 'N/A')} {user_info.get('LastName', 'N/A')}")
            else:
                print("User info request failed")
                
        else:
            print("ERROR: Failed to get access token from refresh token")
            print("Please check your refresh token and try again")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
