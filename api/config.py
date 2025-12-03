import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))

# Storage paths
VIDEOS_DIR = DATA_DIR / "videos"
BACKGROUNDS_DIR = DATA_DIR / "backgrounds"
DB_DIR = DATA_DIR / "db"
SESSIONS_DIR = DATA_DIR / "sessions"
LOGS_DIR = DATA_DIR / "logs"

# Create directories if not exist
for dir_path in [VIDEOS_DIR, BACKGROUNDS_DIR, DB_DIR, SESSIONS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_URL = f"sqlite:///{DB_DIR}/quran_video.db"

# API Keys
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Server
PORT = int(os.getenv("PORT", 8080))

# Quran API
QURAN_API_BASE = "https://api.alquran.cloud/v1"

# Video settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30

# Qari options
QARI_OPTIONS = {
    "alafasy": "ar.alafasy",
    "abdulbasit": "ar.abdulbasit", 
    "sudais": "ar.abdurrahmaansudais",
    "husary": "ar.husary",
    "minshawi": "ar.minshawi"
}
