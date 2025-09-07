# Portfolio Insight & Research Platform

A comprehensive FastAPI-based platform for portfolio management and investment research, featuring real-time price updates, data scraping, and advanced analytics. Built with industry-standard architecture for scalability and performance.

## 🚀 Features

### Core Portfolio Management
- **Portfolio CRUD**: Create, read, update, and delete portfolios
- **Stock Holdings**: Manage individual stock holdings within portfolios
- **User Management**: Multi-user portfolio management
- **Portfolio Analytics**: Real-time portfolio summaries and market value calculations

### Data Scraping & Ingestion
- **Capitol Hill Trades**: Scrape congressional trading data using Firecrawl
- **Yahoo Finance Integration**: Real-time and historical stock data via yfinance
- **Automated Data Ingestion**: Store scraped data in structured database
- **Sample Portfolio Creation**: Generate portfolios from scraped data

### Real-time Price System
- **Live Price Updates**: Real-time stock price streaming via WebSockets
- **Redis Caching**: High-performance price data storage
- **Industry-Standard Architecture**: 5-minute real-time + 24-hour minute data
- **Price History**: Comprehensive historical price tracking

### Advanced Features
- **WebSocket Streaming**: Live price updates for real-time dashboards
- **RESTful API**: Clean, well-documented API endpoints
- **Comprehensive Testing**: Full test suite with 100% functionality coverage
- **Database Migrations**: Alembic for schema management
- **Graceful Degradation**: Works with or without Redis

## 🏗️ Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation and serialization

### Database & Storage
- **SQLite**: Primary database for development (easily switchable to PostgreSQL)
- **Redis**: In-memory data store for real-time price caching
- **SQLAlchemy**: Python ORM for database operations
- **Alembic**: Database migration tool

### Data Sources & Scraping
- **Firecrawl**: Web scraping service for Capitol Hill Trades
- **yfinance**: Yahoo Finance API for stock data
- **requests**: HTTP library for web requests
- **BeautifulSoup4**: HTML parsing for web scraping
- **pandas**: Data manipulation and analysis

### Real-time & Caching
- **Redis**: Real-time price caching and time-series data
- **WebSockets**: Bidirectional real-time communication
- **JSON**: Data serialization for real-time updates

### Testing & Development
- **pytest**: Testing framework
- **requests**: HTTP client for API testing
- **websockets**: WebSocket client for testing

### Development Tools
- **Git**: Version control
- **GitHub**: Code repository and collaboration
- **Python Virtual Environment**: Dependency isolation

## 📁 Project Structure

```
portfolio-insight-platform/
├── app/
│   ├── api/                          # API endpoints
│   │   ├── portfolio.py              # Portfolio CRUD endpoints
│   │   ├── data_ingestion.py         # Data scraping endpoints
│   │   └── real_time_prices.py       # Real-time price endpoints + WebSocket
│   ├── core/                         # Core configuration
│   │   └── config.py                 # Application settings
│   ├── db/                           # Database configuration
│   │   └── database.py               # SQLAlchemy engine and session
│   ├── models/                       # SQLAlchemy models
│   │   ├── models.py                 # Core database models
│   │   └── price_models.py           # Price data models
│   ├── schemas/                      # Pydantic schemas
│   │   └── schemas.py                # API request/response schemas
│   ├── services/                     # Business logic
│   │   ├── portfolio_service.py      # Portfolio management logic
│   │   ├── data_scraper.py           # Web scraping services
│   │   ├── data_ingestion.py         # Data storage services
│   │   └── real_time_price_service.py # Real-time price management
│   └── main.py                       # FastAPI application entry point
├── alembic/                          # Database migrations
├── tests/                            # Test files
│   └── test_portfolio.py             # Portfolio API tests
├── test_all_functionalities.py       # Comprehensive test suite
├── test_data_scraping.py             # Data scraping tests
├── test_real_time_prices.py          # Real-time price tests
├── REAL_TIME_PRICES_GUIDE.md         # Architecture documentation
├── requirements.txt                  # Python dependencies
├── alembic.ini                       # Alembic configuration
├── env.example                       # Environment variables template
└── README.md                         # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Redis** (for real-time features)
- **Git**

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/lesleyzhao/portfolio-insight-platform.git
cd portfolio-insight-platform
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp env.example .env
# Edit .env with your configuration
```

5. **Set up Redis (for real-time features):**
```bash
# macOS with Homebrew
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

6. **Set up the database:**
```bash
# Run migrations
alembic upgrade head
```

7. **Run the application:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Endpoints

#### Portfolio Management
- `POST /api/v1/portfolios` - Create a new portfolio
- `GET /api/v1/portfolios?user_id={user_id}` - List portfolios for a user
- `GET /api/v1/portfolios/{portfolio_id}?user_id={user_id}` - Get specific portfolio
- `PUT /api/v1/portfolios/{portfolio_id}?user_id={user_id}` - Update portfolio
- `DELETE /api/v1/portfolios/{portfolio_id}?user_id={user_id}` - Delete portfolio

#### Stock Management
- `GET /api/v1/portfolios/{portfolio_id}/stocks?user_id={user_id}` - Get portfolio stocks
- `POST /api/v1/portfolios/{portfolio_id}/stocks?user_id={user_id}` - Add stock to portfolio
- `PATCH /api/v1/portfolios/{portfolio_id}/stocks/{holding_id}?user_id={user_id}` - Update stock holding
- `DELETE /api/v1/portfolios/{portfolio_id}/stocks/{holding_id}?user_id={user_id}` - Remove stock

#### Data Scraping
- `GET /api/v1/data/scrape/capitol-hill-trades` - Scrape Capitol Hill Trades
- `GET /api/v1/data/scrape/stock-data/{ticker}` - Scrape stock data for ticker
- `POST /api/v1/data/ingest/tickers` - Ingest ticker data
- `POST /api/v1/data/ingest/sample-portfolios` - Create sample portfolios

#### Real-time Prices
- `POST /api/v1/prices/update` - Update real-time prices
- `GET /api/v1/prices/realtime/{ticker}` - Get current price
- `GET /api/v1/prices/history/{ticker}` - Get price history (Redis)
- `GET /api/v1/prices/historical/{ticker}` - Get historical prices (Database)
- `GET /api/v1/prices/market-summary` - Get market summary
- `WS /api/v1/prices/ws/{ticker}` - WebSocket for live price updates

#### Portfolio Analytics
- `GET /api/v1/data/portfolios/{portfolio_id}/summary` - Get portfolio summary

## 🏛️ Database Schema

### Core Tables
- **`users`** - User accounts and authentication
- **`tickers`** - Stock ticker master data
- **`portfolios`** - Portfolio metadata and settings
- **`holdings_current`** - Current stock holdings in portfolios
- **`prices_daily`** - Daily closing stock prices

### Real-time Data Storage
- **Redis Sorted Sets**: Time-series price data (last 5 minutes)
- **Redis Hash**: Current price data (last 24 hours)
- **PostgreSQL**: Historical daily prices (permanent storage)

## 🔄 Real-time Architecture

### Data Flow
```
External APIs → FastAPI → Redis (Real-time) → PostgreSQL (Historical)
     ↓              ↓
WebSocket ←─── Client Dashboard
```

### Storage Strategy
- **Real-time (Redis)**: Last 5 minutes at 1-second intervals
- **Short-term (Redis)**: Last 24 hours at 1-minute intervals  
- **Historical (PostgreSQL)**: Daily closing prices (permanent)

### WebSocket Streaming
- **Endpoint**: `ws://localhost:8000/api/v1/prices/ws/{ticker}`
- **Update Frequency**: 1 second
- **Data Format**: JSON with price, change, volume, timestamp

## 🧪 Testing

### Run All Tests
```bash
python test_all_functionalities.py
```

### Run Specific Test Suites
```bash
# Portfolio API tests
pytest tests/test_portfolio.py

# Data scraping tests
python test_data_scraping.py

# Real-time price tests
python test_real_time_prices.py
```

### Test Coverage
- ✅ **Portfolio CRUD** - All operations tested
- ✅ **Data Scraping** - Capitol Hill Trades + Yahoo Finance
- ✅ **Real-time Prices** - Redis integration + WebSocket
- ✅ **Portfolio Analytics** - Summary calculations
- ✅ **Error Handling** - Graceful degradation

## 🔧 Development

### Database Migrations

**Create a new migration:**
```bash
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback migrations:**
```bash
alembic downgrade -1
```

### Environment Variables

Create a `.env` file with:
```env
DATABASE_URL=sqlite:///./portfolio.db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

### Adding New Features

1. **API Endpoints**: Add to `app/api/`
2. **Business Logic**: Add to `app/services/`
3. **Database Models**: Add to `app/models/`
4. **API Schemas**: Add to `app/schemas/`
5. **Tests**: Add comprehensive tests
6. **Documentation**: Update README and API docs

## 🚀 Production Deployment

### Prerequisites
- **PostgreSQL** (for production database)
- **Redis** (for real-time features)
- **Python 3.8+**
- **Nginx** (reverse proxy)
- **Gunicorn** (WSGI server)

### Environment Setup
```bash
# Install production dependencies
pip install gunicorn

# Set production environment variables
export DATABASE_URL=postgresql://user:pass@localhost/portfolio_db
export REDIS_URL=redis://localhost:6379
export SECRET_KEY=your-production-secret-key
```

### Run Production Server
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📊 Performance & Scalability

### Redis Performance
- **Memory Usage**: ~300KB per ticker (5 minutes of data)
- **Throughput**: 100,000+ operations per second
- **Latency**: Sub-millisecond response times

### Database Optimization
- **Indexes**: Optimized for portfolio and price queries
- **Connection Pooling**: SQLAlchemy connection management
- **Query Optimization**: Efficient portfolio calculations

### WebSocket Scaling
- **Connection Management**: Efficient WebSocket handling
- **Memory Usage**: Minimal per connection
- **Broadcasting**: Real-time updates to all connected clients

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run the test suite**: `python test_all_functionalities.py`
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to the branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **Redis** - In-memory data store
- **yfinance** - Yahoo Finance data
- **Firecrawl** - Web scraping service
- **SQLAlchemy** - Python ORM
- **Alembic** - Database migrations

## 📞 Support

For support, email support@portfolio-insight.com or create an issue on GitHub.

---

**Built with ❤️ for the investment community**