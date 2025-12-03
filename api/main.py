from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from api.routers import videos, generate, settings, stats, tiktok, caption
from api.database import init_db
from api.scheduler import init_scheduler
from api.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    init_db()
    init_scheduler()
    yield
    # Shutdown


app = FastAPI(
    title="Quran Video Generator",
    description="Auto-generate video quotes Al-Quran untuk TikTok",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (must be before static files mount)
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(generate.router, prefix="/api/generate", tags=["Generate"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(stats.router, prefix="/api/stats", tags=["Stats"])
app.include_router(tiktok.router, prefix="/api/tiktok", tags=["TikTok"])
app.include_router(caption.router, prefix="/api/caption", tags=["Caption"])

# Serve static files (frontend) - must be last
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
