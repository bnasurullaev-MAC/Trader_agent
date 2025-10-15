#!/usr/bin/env python3
"""
Test script for TradeStation API endpoints.

This script demonstrates the specific API endpoints mentioned:
1. POST https://signin.tradestation.com/oauth/token - for authentication
2. GET https://api.tradestation.com/v3/marketdata/barcharts/AAPL - for historical data
"""

import os
import sys
from pathlib import Path
import requests
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_refresh_token():
    """Test the refresh token endpoint."""
    print("=" * 60)
    print("TESTING REFRESH TOKEN ENDPOINT")
    print("=" * 60)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Get credentials from environment
    client_id = os.getenv("TRADESTATION_CLIENT_ID")
    client_secret = os.getenv("TRADESTATION_CLIENT_SECRET")
    refresh_token = os.getenv("TRADESTATION_CLIENT_REFRESH")
    
    if not client_id or not client_secret or not refresh_token:
        print("Missing credentials!")
        print("Set TRADESTATION_CLIENT_ID, TRADESTATION_CLIENT_SECRET, and TRADESTATION_CLIENT_REFRESH environment variables")
        return None
    
    print(f"Client ID: {client_id}")
    print(f"Refresh Token: {refresh_token[:20]}...")
    
    print("\nTradeStation refresh token endpoint:")
    print("POST https://signin.tradestation.com/oauth/token")
    
    # Show refresh token request structure
    token_data = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token
    }
    
    print(f"\nRefresh token request data (POST body - form encoded):")
    print("grant_type=refresh_token&client_id=...&client_secret=...&refresh_token=...")
    print(f"\nActual data being sent:")
    print(json.dumps(token_data, indent=2))
    
    # Actually make the request to get access token
    print(f"\nMaking actual request to get access token...")
    try:
        import requests
        
        response = requests.post(
            "https://signin.tradestation.com/oauth/token",
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            access_token_data = response.json()
            access_token = access_token_data.get('access_token')
            print(f"SUCCESS! Got access token: {access_token[:20]}...")
            return access_token
        else:
            print(f"ERROR: {response.text}")
            return None
            
    except Exception as e:
        print(f"Request failed: {e}")
        return None
    
    return True

def test_barcharts_endpoint(access_token=None):
    """Test the barcharts endpoint."""
    print("\n" + "=" * 60)
    print("TESTING BARCHARTS ENDPOINT")
    print("=" * 60)
    
    # Barcharts endpoint
    symbol = "AAPL"
    endpoint = f"https://api.tradestation.com/v3/marketdata/barcharts/{symbol}"
    
    # Parameters as specified - using more recent date range to get more data
    params = {
        'interval': 1,
        'unit': 'Daily',
        'startdate': '2023-01-01T00:00:00Z',
        'enddate': '2024-12-31T23:59:59Z'
    }
    
    print(f"Endpoint: {endpoint}")
    print(f"Parameters: {params}")
    
    # Build full URL
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{endpoint}?{query_string}"
    print(f"Full URL: {full_url}")
    
    if access_token:
        print(f"\nUsing access token: {access_token[:20]}...")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print(f"Making GET request to: {full_url}")
        print(f"Headers: Authorization: Bearer {access_token[:20]}...")
        
        try:
            response = requests.get(full_url, headers=headers)
            print(f"\nResponse Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("SUCCESS! Historical data retrieved:")
                print("=" * 50)
                print("FULL RESPONSE DATA:")
                print("=" * 50)
                
                # Show the complete response
                print(json.dumps(data, indent=2))
                
                # Also show a summary if Bars exist
                if 'Bars' in data:
                    bars = data['Bars']
                    print(f"\nSUMMARY:")
                    print(f"Number of bars: {len(bars)}")
                    if bars:
                        print(f"Date range: {bars[0].get('TimeStamp', 'N/A')} to {bars[-1].get('TimeStamp', 'N/A')}")
                        print(f"Latest price: ${bars[-1].get('Close', 'N/A')}")
                        
                        # Show first few and last few bars for overview
                        print(f"\nFIRST 3 BARS:")
                        for i, bar in enumerate(bars[:3]):
                            print(f"  Bar {i+1}: {bar.get('TimeStamp', 'N/A')} - Open: ${bar.get('Open', 'N/A')}, High: ${bar.get('High', 'N/A')}, Low: ${bar.get('Low', 'N/A')}, Close: ${bar.get('Close', 'N/A')}, Volume: {bar.get('TotalVolume', 'N/A')}")
                        
                        if len(bars) > 6:
                            print(f"\n... ({len(bars)-6} more bars) ...")
                            
                        print(f"\nLAST 3 BARS:")
                        for i, bar in enumerate(bars[-3:]):
                            bar_num = len(bars) - 3 + i + 1
                            print(f"  Bar {bar_num}: {bar.get('TimeStamp', 'N/A')} - Open: ${bar.get('Open', 'N/A')}, High: ${bar.get('High', 'N/A')}, Low: ${bar.get('Low', 'N/A')}, Close: ${bar.get('Close', 'N/A')}, Volume: {bar.get('TotalVolume', 'N/A')}")
                else:
                    print("\nNo 'Bars' key found in response")
                    print("Available keys:", list(data.keys()) if isinstance(data, dict) else "Not a dict")
            else:
                print(f"ERROR: {response.text}")
                
        except Exception as e:
            print(f"Request failed: {e}")
    else:
        print("\nNo access token available - cannot test barcharts endpoint")
        print("Make sure refresh token is working first")

def test_with_our_client():
    """Test using our TradeStation client."""
    print("\n" + "=" * 60)
    print("TESTING WITH OUR TRADESTATION CLIENT")
    print("=" * 60)
    
    try:
        from tradestation_api import create_tradestation_client
        
        # Create client
        client = create_tradestation_client()
        
        print("TradeStation client created successfully!")
        
        # Show barcharts method
        print(f"\nBarcharts method available:")
        print(f"   client.get_historical_data('AAPL', interval=1, unit='Daily', ...)")
        
        # Test authentication structure
        print(f"\nRefresh token endpoint: {client.config.auth_base_url}{client.config.token_endpoint}")
        print(f"API endpoint: {client.config.base_url}{client.config.marketdata_endpoint}/barcharts/")
        
        # Actually try to get historical data with our client
        print(f"\nTrying to get historical data with our client...")
        try:
            data = client.get_historical_data(
                symbol='AAPL',
                interval=1,
                unit='Daily',
                start_date='2023-01-01T00:00:00Z',
                end_date='2023-12-31T23:59:59Z'
            )
            
            if data:
                print("SUCCESS! Got data from our client:")
                print(json.dumps(data, indent=2))
            else:
                print("No data returned from client")
                
        except Exception as e:
            print(f"Error getting data from client: {e}")
        
        return client
        
    except Exception as e:
        print(f"Error creating client: {e}")
        return None

def main():
    """Main test function."""
    print("TradeStation API Endpoints Test")
    print("Testing the specific endpoints:")
    print("1. POST https://signin.tradestation.com/oauth/token (get access token from refresh token)")
    print("2. GET https://api.tradestation.com/v3/marketdata/barcharts/AAPL (use access token)")
    
    # Test refresh token and get access token
    access_token = test_refresh_token()
    
    # Test barcharts endpoint with the access token
    test_barcharts_endpoint(access_token)
    
    # Test with our client
    client = test_with_our_client()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Set your TradeStation API credentials:")
    print("   export TRADESTATION_CLIENT_ID='your-client-id'")
    print("   export TRADESTATION_CLIENT_SECRET='your-client-secret'")
    print("   export TRADESTATION_CLIENT_REFRESH='your-refresh-token'")
    print()
    print("2. The client will automatically get access token from refresh token")
    print("3. Start making API calls immediately")
    print()
    print("Example Python code:")
    print("```python")
    print("from tradestation_api import create_tradestation_client")
    print("client = create_tradestation_client()")
    print("data = client.get_historical_data('AAPL', interval=1, unit='Daily')")
    print("```")

if __name__ == "__main__":
    main()
