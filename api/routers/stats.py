from fastapi import APIRouter, Depends
import shutil
from sqlalchemy.orm import Session

from api.config import DATA_DIR
from api.database import get_db
from api.repositories.video_repository import VideoRepository
from api.repositories.tiktok_repository import TikTokRepository

router = APIRouter()


@router.get("")
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    video_repo = VideoRepository(db)
    tiktok_repo = TikTokRepository(db)
    
    # Get disk usage
    total, used, free = shutil.disk_usage(DATA_DIR)
    
    # Get video stats
    total_videos = video_repo.count()
    completed_videos = video_repo.count_by_status("completed")
    total_posted = tiktok_repo.count_successful_posts()
    videos_size = video_repo.get_total_size()
    
    return {
        "total_videos": total_videos,
        "completed_videos": completed_videos,
        "total_posted": total_posted,
        "storage": {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "videos_size_mb": round(videos_size / (1024**2), 2)
        },
        "low_storage_warning": free < 1024**3  # Less than 1GB
    }
