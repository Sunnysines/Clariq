"""Clariq Backend – FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database.session import init_db
from app.api.health import router as health_router
from app.api.analyze import router as analyze_router

settings = get_settings()

# --- Logging ---
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("clariq")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info("Clariq backend starting …")
    await init_db()
    logger.info("Database initialised.")
    yield
    logger.info("Clariq backend shutting down …")


app = FastAPI(
    title="Clariq API",
    description="Evidence-powered decision intelligence.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
app.include_router(health_router, tags=["Health"])
app.include_router(analyze_router)
