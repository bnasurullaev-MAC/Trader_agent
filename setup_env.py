#!/usr/bin/env python3
"""
Environment setup script for TradeStation API credentials.

This script helps you set up your TradeStation API credentials in the .env file.
"""

import os
from pathlib import Path

def setup_credentials():
    """Set up all API credentials in .env file."""
    print("=" * 60)
    print("API CREDENTIALS SETUP")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please run the setup first to create the .env file.")
        return False
    
    print("📋 Setting up API credentials...")
    print("This will help you configure both RAG system and TradeStation API credentials.")
    print()
    
    # Get RAG system credentials
    print("🤖 RAG SYSTEM CREDENTIALS:")
    print("You can get your Gemini API key from: https://makersuite.google.com/app/apikey")
    gemini_key = input("Enter your Google Gemini API key (or press Enter to skip): ").strip()
    
    # Get TradeStation credentials
    print("\n📈 TRADESTATION API CREDENTIALS:")
    print("You can get these from: https://developers.tradestation.com/")
    client_id = input("Enter your TradeStation Client ID (or press Enter to skip): ").strip()
    client_secret = input("Enter your TradeStation Client Secret (or press Enter to skip): ").strip()
    
    if not any([gemini_key, client_id, client_secret]):
        print("❌ At least one credential is required!")
        return False
    
    # Read current .env content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace placeholder values
    if gemini_key:
        content = content.replace("your-gemini-api-key-here", gemini_key)
    if client_id:
        content = content.replace("your-client-id-here", client_id)
    if client_secret:
        content = content.replace("your-client-secret-here", client_secret)
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Credentials updated in .env file!")
    
    # Test loading environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Verify credentials are loaded
        loaded_gemini_key = os.getenv("GEMINI_KEY")
        loaded_client_id = os.getenv("TRADESTATION_CLIENT_ID")
        loaded_client_secret = os.getenv("TRADESTATION_CLIENT_SECRET")
        
        success = True
        if gemini_key and loaded_gemini_key != gemini_key:
            print("⚠️  Gemini API key loaded but values don't match")
            success = False
        if client_id and loaded_client_id != client_id:
            print("⚠️  TradeStation Client ID loaded but values don't match")
            success = False
        if client_secret and loaded_client_secret != client_secret:
            print("⚠️  TradeStation Client Secret loaded but values don't match")
            success = False
        
        if success:
            print("✅ Environment variables loaded successfully!")
            return True
        else:
            return False
            
    except ImportError:
        print("⚠️  python-dotenv not installed. Install it with: pip install python-dotenv")
        return False

def test_clients():
    """Test both RAG and TradeStation clients with loaded credentials."""
    print("\n" + "=" * 60)
    print("TESTING CLIENTS")
    print("=" * 60)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Test RAG system
        print("🤖 Testing RAG System...")
        try:
            from src.config import SETTINGS
            from src.gemini_client import create_gemini_client
            
            print(f"✅ RAG system configuration loaded!")
            print(f"   Qdrant: {SETTINGS.qdrant_host}:{SETTINGS.qdrant_port}")
            print(f"   Collection: {SETTINGS.collection}")
            print(f"   Embedding Model: {SETTINGS.embedding_model}")
            
            # Test Gemini client if API key is available
            gemini_key = os.getenv("GEMINI_KEY")
            if gemini_key and gemini_key != "your-gemini-api-key-here":
                try:
                    gemini_client = create_gemini_client()
                    print("✅ Gemini client created successfully!")
                except Exception as e:
                    print(f"⚠️  Gemini client test failed: {e}")
            else:
                print("⚠️  Gemini API key not configured")
                
        except Exception as e:
            print(f"⚠️  RAG system test failed: {e}")
        
        # Test TradeStation client
        print("\n📈 Testing TradeStation API...")
        try:
            # Add Tradestation directory to path
            import sys
            sys.path.insert(0, str(Path("Tradestation")))
            
            from tradestation_api import create_tradestation_client
            
            # Create client
            client = create_tradestation_client()
            
            print("✅ TradeStation client created successfully!")
            
            # Show authorization URL
            auth_url = client.get_auth_url()
            print(f"📋 Authorization URL: {auth_url}")
            
            print("\n📋 TradeStation next steps:")
            print("1. Visit the authorization URL above")
            print("2. Complete the OAuth flow")
            print("3. Get the authorization code")
            print("4. Use client.authenticate(auth_code) to get access token")
            print("5. Start making API calls!")
            
        except Exception as e:
            print(f"⚠️  TradeStation client test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing TradeStation client: {e}")
        return False

def main():
    """Main setup function."""
    print("API Credentials Environment Setup")
    print("This script will help you configure your RAG system and TradeStation API credentials.")
    print()
    
    # Setup credentials
    if setup_credentials():
        # Test clients
        test_clients()
        
        print("\n" + "=" * 60)
        print("SETUP COMPLETE!")
        print("=" * 60)
        print("Your API credentials are now configured.")
        print("You can now use both the RAG system and TradeStation integration.")
        
    else:
        print("\n❌ Setup failed. Please check your credentials and try again.")

if __name__ == "__main__":
    main()
