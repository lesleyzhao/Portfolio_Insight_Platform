# Portfolio Insight & Research Platform

A FastAPI-based platform for portfolio management and investment research, designed to provide users with actionable insights into their investment portfolios.

## Features

- **Portfolio Management**: Create, read, update, and delete portfolios
- **Stock Holdings**: Manage individual stock holdings within portfolios
- **RESTful API**: Clean, well-documented API endpoints
- **PostgreSQL Database**: Robust relational database for structured data
- **Database Migrations**: Alembic for database schema management

## Technology Stack

- **Web Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Validation**: Pydantic

## Project Structure

```
portfolio-insight-platform/
├── app/
│   ├── api/                 # API endpoints
│   ├── core/               # Core configuration
│   ├── db/                 # Database configuration
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   └── main.py             # FastAPI application
├── alembic/                # Database migrations
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd portfolio-insight-platform
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your database credentials
```

5. Set up the database:
```bash
# Create the database in PostgreSQL
createdb portfolio_db

# Run migrations
alembic upgrade head
```

6. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## API Endpoints

### Portfolio Management

- `POST /api/v1/portfolios` - Create a new portfolio
- `GET /api/v1/portfolios` - List all portfolios for a user
- `GET /api/v1/portfolios/{portfolio_id}` - Get a specific portfolio
- `PUT /api/v1/portfolios/{portfolio_id}` - Update a portfolio
- `DELETE /api/v1/portfolios/{portfolio_id}` - Delete a portfolio

### Stock Management

- `GET /api/v1/portfolios/{portfolio_id}/stocks` - Get all stocks in a portfolio
- `POST /api/v1/portfolios/{portfolio_id}/stocks` - Add a stock to a portfolio
- `PATCH /api/v1/portfolios/{portfolio_id}/stocks/{holding_id}` - Update a stock holding
- `DELETE /api/v1/portfolios/{portfolio_id}/stocks/{holding_id}` - Remove a stock from a portfolio

## Database Schema

The application uses the following main tables:
- `users` - User accounts
- `tickers` - Stock ticker master data
- `portfolios` - Portfolio metadata
- `holdings_current` - Current stock holdings
- `prices_daily` - Daily stock prices

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migrations:
```bash
alembic downgrade -1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.
