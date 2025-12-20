"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from artomate.api.routes import analytics, assets, health, jobs, products, telegram, metrics, upload, viral
from artomate.core.config import get_config
from artomate.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    Args:
        app: FastAPI application

    Yields:
        None
    """
    # Startup
    logger.info("Starting Artomate API...")
    config = get_config()
    config.ensure_directories()

    # Ensure database is initialized
    try:
        init_db()
        logger.info("Database ready")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Artomate API...")


# Create FastAPI app
config = get_config()

app = FastAPI(
    title="Artomate API",
    description="Content-to-Commerce Automation System",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(viral.router, prefix="/api/viral", tags=["Viral Content"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(telegram.router, prefix="/telegram", tags=["Telegram"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Artomate API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
