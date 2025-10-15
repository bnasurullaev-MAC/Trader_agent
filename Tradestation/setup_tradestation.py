#!/usr/bin/env python3
"""
TradeStation API Setup Script

This script helps you set up TradeStation API integration for trading applications.
It guides you through the process of obtaining API credentials and configuring the environment.
"""

import os
import sys
from pathlib import Path

def print_header():
    """Print setup header."""
    print("=" * 80)
    print("TRADESTATION API SETUP")
    print("=" * 80)
    print("This script will help you set up TradeStation API integration")
    print("to enable real-time market data queries and trading operations.")
    print()

def print_steps():
    """Print setup steps."""
    print("SETUP STEPS:")
    print("=" * 50)
    print("1. Create a TradeStation account (if you don't have one)")
    print("2. Register your application with TradeStation")
    print("3. Obtain API credentials (Client ID and Client Secret)")
    print("4. Set environment variables")
    print("5. Test the integration")
    print()

def print_account_info():
    """Print TradeStation account information."""
    print("TRADESTATION ACCOUNT SETUP:")
    print("=" * 40)
    print("• Visit: https://www.tradestation.com/")
    print("• Create a free account or sign in to existing account")
    print("• Note: You may need to complete identity verification")
    print("• Paper trading accounts are available for testing")
    print()

def print_api_registration():
    """Print API registration instructions."""
    print("API APPLICATION REGISTRATION:")
    print("=" * 40)
    print("1. Go to: https://developers.tradestation.com/")
    print("2. Sign in with your TradeStation account")
    print("3. Click 'Create New App' or 'Register Application'")
    print("4. Fill out the application form:")
    print("   • App Name: TradeStation API Client")
    print("   • Description: API integration for trading applications")
    print("   • Redirect URI: http://localhost:8080/callback")
    print("   • Scopes: Select 'read' and 'write' permissions")
    print("5. Submit the application")
    print("6. Copy your Client ID and Client Secret")
    print()

def get_credentials():
    """Get API credentials from user."""
    print("ENTER YOUR API CREDENTIALS:")
    print("=" * 40)
    
    client_id = input("Enter your TradeStation Client ID: ").strip()
    if not client_id:
        print("❌ Client ID is required!")
        return None, None
    
    client_secret = input("Enter your TradeStation Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret is required!")
        return None, None
    
    return client_id, client_secret

def create_env_file(client_id: str, client_secret: str):
    """Create .env file with TradeStation credentials."""
    env_content = f"""# TradeStation API Configuration
TRADESTATION_CLIENT_ID={client_id}
TRADESTATION_CLIENT_SECRET={client_secret}
TRADESTATION_REDIRECT_URI=http://localhost:8080/callback
TRADESTATION_USE_SANDBOX=true

# Additional configuration (optional)
# TRADESTATION_BASE_URL=https://api.tradestation.com
# TRADESTATION_SANDBOX_URL=https://sim-api.tradestation.com
"""
    
    env_file = Path(".env")
    
    # Check if .env already exists
    if env_file.exists():
        print(f"\n⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Skipping .env file creation.")
            return False
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created .env file with TradeStation credentials")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_integration():
    """Test the TradeStation integration."""
    print("\nTESTING INTEGRATION:")
    print("=" * 30)
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from tradestation_integration import create_tradestation_integration
        
        integration = create_tradestation_integration()
        auth_url = integration.get_auth_url()
        
        print("✅ TradeStation integration created successfully!")
        print(f"📋 Authorization URL: {auth_url}")
        print("\nTo complete setup:")
        print("1. Run your application")
        print("2. Visit the authorization URL")
        print("3. Enter the authorization code")
        print("4. Test with market data queries")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        print("\nPossible issues:")
        print("• Missing environment variables")
        print("• Invalid API credentials")
        print("• Network connectivity issues")
        return False

def print_next_steps():
    """Print next steps."""
    print("\nNEXT STEPS:")
    print("=" * 20)
    print("1. Install dependencies: pip install requests")
    print("2. Use the integration in your application")
    print("3. Authenticate with TradeStation")
    print("4. Start making API calls for market data and trading")
    print()
    print("EXAMPLE USAGE:")
    print("• integration.get_quote_for_symbol('AAPL')")
    print("• integration.get_historical_data('TSLA')")
    print("• integration.get_market_status()")
    print("• integration.get_account_info()")
    print()

def main():
    """Main setup function."""
    print_header()
    
    # Check if already configured
    if os.getenv("TRADESTATION_CLIENT_ID") and os.getenv("TRADESTATION_CLIENT_SECRET"):
        print("✅ TradeStation API already configured!")
        print(f"Client ID: {os.getenv('TRADESTATION_CLIENT_ID')}")
        
        test = input("\nTest the integration? (y/N): ").strip().lower()
        if test == 'y':
            test_integration()
        return
    
    print_steps()
    print_account_info()
    print_api_registration()
    
    # Get credentials
    client_id, client_secret = get_credentials()
    if not client_id or not client_secret:
        print("❌ Setup cancelled - credentials required")
        return
    
    # Create .env file
    if create_env_file(client_id, client_secret):
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("⚠️  python-dotenv not installed. Set environment variables manually:")
            print(f"export TRADESTATION_CLIENT_ID={client_id}")
            print(f"export TRADESTATION_CLIENT_SECRET={client_secret}")
    
    # Test integration
    test_integration()
    print_next_steps()

if __name__ == "__main__":
    main()
