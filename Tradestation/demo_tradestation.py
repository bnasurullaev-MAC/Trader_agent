#!/usr/bin/env python3
"""
Demo script for TradeStation API integration.

This script demonstrates how to use the TradeStation API integration
for real-time market data queries and trading operations.
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Demo the TradeStation integration."""
    print("TradeStation API Integration Demo")
    print("=" * 50)
    
    try:
        # Import with absolute path to avoid relative import issues
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from tradestation_integration import create_tradestation_integration
        
        # Create integration
        print("Creating TradeStation integration...")
        integration = create_tradestation_integration()
        
        # Get authorization URL
        auth_url = integration.get_auth_url()
        print(f"Integration created successfully!")
        print(f"\nAuthorization URL: {auth_url}")
        
        print("\nTo use the TradeStation integration:")
        print("1. Visit the authorization URL above")
        print("2. Complete the OAuth flow")
        print("3. Get the authorization code")
        print("4. Use integration.authenticate(auth_code)")
        print("5. Query market data with integration.process_market_query()")
        
        # Example usage (requires authentication)
        print("\nExample usage after authentication:")
        print("• integration.get_quote_for_symbol('AAPL')")
        print("• integration.get_historical_data('AAPL')")
        print("• integration.get_market_status()")
        print("• integration.get_account_info()")
        print("• integration.process_market_query('AAPL quote')")
        
        # Interactive demo
        print("\n" + "=" * 50)
        print("INTERACTIVE DEMO")
        print("=" * 50)
        
        # Check if user wants to authenticate
        auth_choice = input("\nWould you like to authenticate now? (y/N): ").strip().lower()
        if auth_choice == 'y':
            print(f"\nPlease visit: {auth_url}")
            auth_code = input("Enter the authorization code: ").strip()
            
            if auth_code:
                if integration.authenticate(auth_code):
                    print("Successfully authenticated!")
                    
                    # Demo market data queries
                    print("\nTesting market data queries...")
                    
                    # Test quote
                    print("\n1. Getting AAPL quote...")
                    result = integration.get_quote_for_symbol('AAPL')
                    if result.get('success'):
                        data = result['data']
                        print(f"   AAPL: ${data.get('last_price', 'N/A')} "
                              f"({data.get('change', 'N/A')}, {data.get('change_percent', 'N/A')})")
                    else:
                        print(f"   Error: {result.get('error', 'Unknown error')}")
                    
                    # Test market status
                    print("\n2. Getting market status...")
                    result = integration.get_market_status()
                    if result.get('success'):
                        print("   Market status retrieved successfully")
                    else:
                        print(f"   Error: {result.get('error', 'Unknown error')}")
                    
                    # Test account info
                    print("\n3. Getting account information...")
                    result = integration.get_account_info()
                    if result.get('success'):
                        accounts = result['data'].get('accounts', [])
                        print(f"   Found {len(accounts)} account(s)")
                    else:
                        print(f"   Error: {result.get('error', 'Unknown error')}")
                    
                else:
                    print("Authentication failed. Please check your authorization code.")
            else:
                print("No authorization code provided.")
        
        print("\n" + "=" * 50)
        print("DEMO COMPLETE")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Set TRADESTATION_CLIENT_ID and TRADESTATION_CLIENT_SECRET environment variables")
        print("2. Installed dependencies: pip install requests")
        print("3. Run setup_tradestation.py for guided setup")

if __name__ == "__main__":
    main()
