from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.portfolio import router as portfolio_router
from app.core.config import settings

app = FastAPI(
    title="Portfolio Insight & Research Platform",
    description="A platform for portfolio management and investment research",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(portfolio_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Portfolio Insight & Research Platform API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
