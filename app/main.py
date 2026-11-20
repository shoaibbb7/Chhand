"""Chhand - FastAPI Application Entry Point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.config import settings
from app.errors import register_error_handlers

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered, meter-aware Hindi poetry and lyric co-writer.",
)

# 1. Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Register Custom Exception Handlers
register_error_handlers(app)

# 3. Register API Routers under /api
app.include_router(api_router, prefix="/api")

# 4. Mount Frontend Static Files for Local Development (Must be after API routes)
PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"
if PUBLIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(PUBLIC_DIR), html=True), name="public")
