from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers import quotes, vehicles, partners, photos
from app.middleware import error_handler, RateLimiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="SwiftValuation AI",
    version="1.0.0",
    lifespan=lifespan
)

allow_all_origins = "*" in settings.ALLOWED_ORIGINS

# Rate limiter
rate_limiter = RateLimiter(max_requests=200, window_seconds=60)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    await rate_limiter.check_rate_limit(request)
    response = await call_next(request)
    return response

# Error handler
app.add_exception_handler(Exception, error_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(quotes.router, prefix="/api/v1/quotes", tags=["quotes"])
app.include_router(vehicles.router, prefix="/api/v1/vehicles", tags=["vehicles"])
app.include_router(partners.router, prefix="/api/v1/partners", tags=["partners"])
app.include_router(photos.router, prefix="/api/v1/photos", tags=["photos"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
