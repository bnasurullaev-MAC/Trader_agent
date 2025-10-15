# TradeStation API Integration Package

A comprehensive Python package for integrating with TradeStation's REST API to enable real-time market data retrieval, account management, and trading operations.

## Features

- **🔐 OAuth 2.0 Authentication** - Secure API access with automatic token refresh
- **📊 Real-time Market Data** - Live quotes, historical data, and market status
- **💼 Account Management** - View balances, positions, and account information
- **📈 Order Management** - Place, cancel, and track orders
- **🤖 Natural Language Queries** - Process market data requests through natural language
- **🛡️ Error Handling** - Comprehensive error handling and logging
- **🧪 Sandbox Support** - Safe testing environment for development

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Required
export TRADESTATION_CLIENT_ID="your-client-id"
export TRADESTATION_CLIENT_SECRET="your-client-secret"

# Optional
export TRADESTATION_REDIRECT_URI="http://localhost:8080/callback"
export TRADESTATION_USE_SANDBOX="true"  # Use sandbox for testing
```

### 3. Setup (Guided)

```bash
python setup_tradestation.py
```

### 4. Demo

```bash
python demo_tradestation.py
```

## File Structure

```
Tradestation/
├── __init__.py                    # Package initialization
├── tradestation_api.py           # Core TradeStation API client
├── tradestation_integration.py   # High-level integration layer
├── setup_tradestation.py         # Guided setup script
├── demo_tradestation.py          # Demo and testing script
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## Usage

### Basic API Client

```python
from tradestation_api import create_tradestation_client

# Create client
client = create_tradestation_client()

# Get authorization URL
auth_url = client.get_auth_url()
print(f"Visit: {auth_url}")

# Authenticate
auth_code = input("Enter authorization code: ")
if client.authenticate(auth_code):
    print("✅ Authenticated successfully!")
    
    # Get market data
    quote = client.get_quote("AAPL")
    print(f"AAPL: ${quote['LastPrice']}")
```

### High-Level Integration

```python
from tradestation_integration import create_tradestation_integration

# Create integration
integration = create_tradestation_integration()

# Authenticate
auth_url = integration.get_auth_url()
# ... authenticate as above ...

# Process natural language queries
result = integration.process_market_query("AAPL quote")
if result['success']:
    data = result['data']
    print(f"AAPL: ${data['last_price']}")

# Get historical data
hist_data = integration.get_historical_data("AAPL", interval="1Day", days_back=30)
```

## API Methods

### Market Data

- `get_quote(symbol)` - Get real-time quote for a symbol
- `get_quotes(symbols)` - Get quotes for multiple symbols
- `get_historical_data(symbol, interval, start_date, end_date)` - Get historical price data
- `get_market_status()` - Get current market status

### Account Management

- `get_accounts()` - Get user's trading accounts
- `get_account_balance(account_id)` - Get account balance and positions
- `get_positions(account_id)` - Get current positions

### Order Management

- `get_orders(account_id, status)` - Get orders for an account
- `place_order(account_id, symbol, quantity, order_type, side, price)` - Place new order
- `cancel_order(account_id, order_id)` - Cancel existing order

### Utility Methods

- `get_user_info()` - Get user information
- `get_auth_url()` - Generate authorization URL
- `authenticate(auth_code)` - Authenticate with authorization code
- `refresh_access_token()` - Refresh expired access token

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TRADESTATION_CLIENT_ID` | Your TradeStation client ID | Required |
| `TRADESTATION_CLIENT_SECRET` | Your TradeStation client secret | Required |
| `TRADESTATION_REDIRECT_URI` | OAuth redirect URI | `http://localhost:8080/callback` |
| `TRADESTATION_USE_SANDBOX` | Use sandbox environment | `true` |

### TradeStation API Endpoints

- **Production**: `https://api.tradestation.com`
- **Sandbox**: `https://sim-api.tradestation.com`

## Authentication Flow

1. **Register Application**: Create app at [TradeStation Developers](https://developers.tradestation.com/)
2. **Get Credentials**: Obtain Client ID and Client Secret
3. **Generate Auth URL**: Use `get_auth_url()` method
4. **User Authorization**: User visits URL and authorizes app
5. **Exchange Code**: Use authorization code with `authenticate()`
6. **Make API Calls**: Start making authenticated requests

## Error Handling

The package includes comprehensive error handling:

```python
try:
    quote = client.get_quote("INVALID")
    if quote:
        print(f"Quote: {quote}")
    else:
        print("No quote data received")
except Exception as e:
    print(f"Error: {e}")
```

## Logging

Enable logging to see detailed API interactions:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Now API calls will show detailed logs
client = create_tradestation_client()
```

## Examples

### Get Stock Quote

```python
from tradestation_integration import create_tradestation_integration

integration = create_tradestation_integration()
# ... authenticate ...

result = integration.get_quote_for_symbol("AAPL")
if result['success']:
    data = result['data']
    print(f"AAPL: ${data['last_price']}")
    print(f"Change: {data['change']} ({data['change_percent']})")
```

### Get Historical Data

```python
hist_data = integration.get_historical_data(
    symbol="AAPL",
    interval="1Day",
    days_back=30
)

if hist_data['success']:
    data = hist_data['data']
    print(f"Retrieved {data['total_bars']} bars")
    for bar in data['recent_bars'][-5:]:  # Last 5 days
        print(f"{bar['datetime']}: ${bar['close']}")
```

### Process Natural Language Query

```python
# Natural language processing
queries = [
    "AAPL quote",
    "What's the price of Tesla?",
    "Get historical data for MSFT",
    "Show me market status"
]

for query in queries:
    result = integration.process_market_query(query)
    if result['success']:
        print(f"Query: {query}")
        print(f"Result: {result['data']}")
```

## Development

### Running Tests

```bash
# Run the demo to test functionality
python demo_tradestation.py

# Run setup to verify configuration
python setup_tradestation.py
```

### Adding New Features

1. Extend `TradeStationAPI` class in `tradestation_api.py`
2. Add corresponding methods in `TradeStationIntegration`
3. Update error handling and logging
4. Test with demo script

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify Client ID and Secret
   - Check redirect URI matches registration
   - Ensure authorization code is valid

2. **API Request Failed**
   - Check network connectivity
   - Verify API endpoint URLs
   - Check rate limits

3. **Token Expired**
   - Tokens auto-refresh, but check refresh token
   - Re-authenticate if refresh fails

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This package is for educational and development purposes. Please review TradeStation's API terms of service for production use.

## Support

- **TradeStation API Documentation**: [https://developers.tradestation.com/](https://developers.tradestation.com/)
- **TradeStation Support**: Contact TradeStation for API support
- **Package Issues**: Check the code and error messages for debugging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Note**: This package requires a TradeStation account and API credentials. Paper trading accounts are recommended for testing.
