# Trader Agent - AI-Powered Trading Assistant

A comprehensive AI trading assistant that combines Retrieval-Augmented Generation (RAG) with TradeStation API integration for intelligent market analysis and trading operations.

## 🚀 Features

### 🤖 RAG System (Retrieval-Augmented Generation)
- **Knowledge Base**: Extensive trading and financial knowledge from 100+ documents
- **Semantic Search**: Advanced vector-based search using Qdrant and SentenceTransformers
- **AI Chat**: Google Gemini-powered conversational AI for trading insights
- **Document Processing**: Support for PDF, DOCX, PPTX, Excel, and text files

### 📈 TradeStation API Integration
- **Real-time Market Data**: Live quotes, historical data, and market status
- **Account Management**: View balances, positions, and account information
- **Order Management**: Place, cancel, and track orders
- **OAuth 2.0 Authentication**: Secure API access with automatic token refresh
- **Direct Access**: Support for refresh token-based authentication

### 🔧 Advanced Features
- **Natural Language Queries**: Process trading requests in plain English
- **Modular Architecture**: Clean separation between RAG system and trading functionality
- **Error Handling**: Comprehensive error handling and logging
- **Sandbox Support**: Safe testing environment for development

## 📁 Project Structure

```
Trader_agent/
├── 📊 RAG System
│   ├── advanced_chatbot.py          # Main chatbot interface
│   ├── chatbot.py                   # Basic chatbot
│   ├── demo_rag.py                  # RAG system demo
│   ├── run_advanced_ingest.py       # Knowledge base ingestion
│   ├── src/                         # Core RAG modules
│   │   ├── config.py                # Configuration management
│   │   ├── embeddings.py            # Text embeddings
│   │   ├── gemini_client.py         # Google Gemini AI client
│   │   ├── rag_query.py             # RAG query processing
│   │   ├── index_qdrant.py          # Vector database operations
│   │   ├── file_parsers.py          # Document parsing
│   │   ├── chunkers.py              # Text chunking utilities
│   │   └── utils.py                 # General utilities
│   └── KB/                          # Knowledge base files
│       └── [100+ trading documents]
│
├── 📈 TradeStation Integration
│   ├── Tradestation/                # TradeStation API package
│   │   ├── tradestation_api.py      # Core API client
│   │   ├── tradestation_integration.py # High-level integration
│   │   ├── setup_tradestation.py    # Guided setup script
│   │   ├── demo_tradestation.py     # Demo and testing
│   │   ├── test_api_endpoints.py    # API endpoint testing
│   │   ├── test_refresh_token.py    # Refresh token testing
│   │   ├── quick_access_example.py  # Direct access example
│   │   ├── requirements.txt         # Dependencies
│   │   └── README.md                # TradeStation documentation
│   └── setup_env.py                 # Environment setup script
│
├── 📋 Configuration
│   ├── requirements.txt             # Main dependencies
│   ├── .env.example                 # Environment variables template
│   └── .gitignore                   # Git ignore rules
│
└── 📚 Documentation
    └── README.md                    # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Git
- TradeStation account (for trading features)
- Google Gemini API key (for AI features)

### 1. Clone the Repository
```bash
git clone https://github.com/bnasurullaev-MAC/Trader_agent.git
cd Trader_agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the environment template and configure your credentials:
```bash
cp .env.example .env
```

Edit `.env` file with your credentials:
```env
# RAG System Configuration
GEMINI_KEY=your-gemini-api-key-here
QDRANT_HOST=localhost
QDRANT_PORT=6333

# TradeStation API Configuration
TRADESTATION_CLIENT_ID=your-client-id
TRADESTATION_CLIENT_SECRET=your-client-secret
TRADESTATION_CLIENT_REFRESH=your-refresh-token
TRADESTATION_USE_SANDBOX=true
```

### 4. Setup TradeStation Integration
```bash
python setup_env.py
```

### 5. Initialize Knowledge Base
```bash
python run_advanced_ingest.py
```

## 🚀 Usage

### RAG System (AI Chat)
```bash
# Run the advanced chatbot
python advanced_chatbot.py

# Or run the basic chatbot
python chatbot.py

# Demo the RAG system
python demo_rag.py
```

### TradeStation Integration
```bash
cd Tradestation

# Test API endpoints
python test_api_endpoints.py

# Test with refresh token
python test_refresh_token.py

# Quick access example
python quick_access_example.py
```

### Python API Usage

#### RAG System
```python
from src.rag_query import RAGQueryProcessor
from src.gemini_client import create_gemini_client

# Initialize RAG system
rag = RAGQueryProcessor()
gemini = create_gemini_client()

# Query the knowledge base
response = rag.process_query("What are leading indicators in trading?")
print(response)
```

#### TradeStation API
```python
from Tradestation.tradestation_integration import create_tradestation_integration

# Create integration (automatically gets access token from refresh token)
integration = create_tradestation_integration()

# Get historical data
data = integration.get_historical_data(
    symbol="AAPL",
    interval=1,
    unit="Daily",
    start_date="2021-07-01T00:00:00Z",
    end_date="2025-07-15T23:59:59Z"
)

# Process natural language queries
result = integration.process_market_query("Get AAPL quote")
```

## 🔑 API Credentials Setup

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Add to `.env` file as `GEMINI_KEY`

### TradeStation API
1. Visit [TradeStation Developers](https://developers.tradestation.com/)
2. Create a new application
3. Get your Client ID and Client Secret
4. Add to `.env` file:
   - `TRADESTATION_CLIENT_ID`
   - `TRADESTATION_CLIENT_SECRET`
   - `TRADESTATION_CLIENT_REFRESH` (if you have a refresh token)

## 📊 Knowledge Base

The system includes an extensive knowledge base with 100+ trading and financial documents covering:
- Leading indicators and economic analysis
- Portfolio management strategies
- Trading psychology and risk management
- Technical analysis and timing
- Trade idea generation
- Market statistics and track records

## 🔧 Configuration Options

### RAG System Configuration
- **Embedding Model**: `sentence-transformers/all-mpnet-base-v2`
- **Vector Database**: Qdrant (local or cloud)
- **AI Model**: Google Gemini 2.5 Flash
- **Chunk Size**: 1000 words with 200 word overlap

### TradeStation Configuration
- **API Version**: v3
- **Authentication**: OAuth 2.0 with refresh token support
- **Environment**: Sandbox (for testing) or Production
- **Rate Limiting**: Automatic with retry logic

## 🧪 Testing

### Run All Tests
```bash
# Test RAG system
python demo_rag.py

# Test TradeStation integration
cd Tradestation
python test_refresh_token.py
python quick_access_example.py
```

### Individual Component Tests
```bash
# Test embeddings
python -c "from src.embeddings import generate_embeddings; print('Embeddings OK')"

# Test Gemini client
python -c "from src.gemini_client import create_gemini_client; print('Gemini OK')"

# Test TradeStation API
python -c "from Tradestation.tradestation_api import create_tradestation_client; print('TradeStation OK')"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading involves risk, and past performance does not guarantee future results. Always do your own research and consider consulting with a financial advisor before making trading decisions.

## 🆘 Support

For support and questions:
- Create an issue in this repository
- Check the documentation in the `Tradestation/README.md` file
- Review the example scripts in the `Tradestation/` directory

## 🔄 Updates

- **v1.0.0**: Initial release with RAG system and TradeStation integration
- **v1.1.0**: Added refresh token support for direct API access
- **v1.2.0**: Enhanced error handling and logging

---

**Built with ❤️ for the trading community**