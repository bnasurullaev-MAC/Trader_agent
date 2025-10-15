#!/usr/bin/env python3
"""
Test script for direct access token retrieval using refresh token.

This script demonstrates how to get an access token directly from a refresh token
without going through the OAuth authorization flow.
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_refresh_token_access():
    """Test getting access token directly from refresh token."""
    print("=" * 60)
    print("TESTING REFRESH TOKEN ACCESS")
    print("=" * 60)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Check if refresh token is available
    refresh_token = os.getenv("TRADESTATION_CLIENT_REFRESH")
    
    if not refresh_token or refresh_token == "your-refresh-token-here":
        print("Missing refresh token!")
        print("Set TRADESTATION_CLIENT_REFRESH environment variable with your refresh token")
        return False
    
    print(f"Refresh token found: {refresh_token[:20]}...")
    
    try:
        from tradestation_api import create_tradestation_client
        
        # Create client - it will automatically try to get access token from refresh token
        print("\nCreating TradeStation client...")
        client = create_tradestation_client()
        
        # Check if we got an access token
        if client.access_token:
            print("SUCCESS! Access token obtained from refresh token")
            print(f"Access token: {client.access_token[:20]}...")
            
            # Test making an API call
            print("\nTesting API call with access token...")
            try:
                # Test market status (doesn't require specific account)
                result = client.get_market_status()
                if result:
                    print("API call successful! Market status retrieved.")
                    return True
                else:
                    print("API call failed - no data returned")
                    return False
            except Exception as e:
                print(f"API call failed: {e}")
                return False
        else:
            print("FAILED! No access token obtained from refresh token")
            return False
            
    except Exception as e:
        print(f"Error creating client: {e}")
        return False

def test_barcharts_with_access_token():
    """Test the barcharts endpoint with access token."""
    print("\n" + "=" * 60)
    print("TESTING BARCHARTS WITH ACCESS TOKEN")
    print("=" * 60)
    
    try:
        from tradestation_api import create_tradestation_client
        
        # Create client
        client = create_tradestation_client()
        
        if not client.access_token:
            print("No access token available. Cannot test barcharts endpoint.")
            return False
        
        print("Testing barcharts endpoint...")
        print("Symbol: AAPL")
        print("Parameters: interval=1, unit=Daily, startdate=2021-07-01T00:00:00Z, enddate=2025-07-15T23:59:59Z")
        
        # Make the API call
        result = client.get_historical_data(
            symbol="AAPL",
            interval=1,
            unit="Daily",
            start_date="2021-07-01T00:00:00Z",
            end_date="2025-07-15T23:59:59Z"
        )
        
        if result:
            print("SUCCESS! Historical data retrieved:")
            print(f"Response keys: {list(result.keys())}")
            
            # Show some sample data
            if 'Bars' in result:
                bars = result['Bars']
                if bars:
                    print(f"Number of bars: {len(bars)}")
                    print("Sample bar data:")
                    print(f"  First bar: {bars[0]}")
                    if len(bars) > 1:
                        print(f"  Last bar: {bars[-1]}")
                else:
                    print("No bar data in response")
            else:
                print("Response structure:")
                print(result)
            
            return True
        else:
            print("FAILED! No data returned from barcharts endpoint")
            return False
            
    except Exception as e:
        print(f"Error testing barcharts: {e}")
        return False

def main():
    """Main test function."""
    print("TradeStation Refresh Token Test")
    print("Testing direct access token retrieval from refresh token")
    print()
    
    # Test refresh token access
    if test_refresh_token_access():
        # Test barcharts endpoint
        test_barcharts_with_access_token()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        print("Your refresh token is working correctly!")
        print("You can now make API calls without going through OAuth flow.")
    else:
        print("\n" + "=" * 60)
        print("SETUP REQUIRED")
        print("=" * 60)
        print("1. Add your refresh token to .env file:")
        print("   TRADESTATION_CLIENT_REFRESH=your-actual-refresh-token")
        print()
        print("2. Run this script again to test")

if __name__ == "__main__":
    main()
