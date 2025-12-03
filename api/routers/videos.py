from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from api.database import get_db
from api.repositories.video_repository import VideoRepository

router = APIRouter()


@router.get("")
async def list_videos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all generated videos with pagination"""
    repo = VideoRepository(db)
    videos, total = repo.get_all(page, limit)
    
    return {
        "videos": [
            {
                "id": v.id,
                "surah": v.surah,
                "ayat": v.ayat,
                "surah_name": v.surah_name,
                "qari": v.qari,
                "duration": v.duration,
                "file_size": v.file_size,
                "status": v.status,
                "created_at": v.created_at.isoformat() if v.created_at else None
            }
            for v in videos
        ],
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/{video_id}")
async def get_video(video_id: str, db: Session = Depends(get_db)):
    """Get video details by ID"""
    repo = VideoRepository(db)
    video = repo.get_by_id(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {
        "id": video.id,
        "surah": video.surah,
        "ayat": video.ayat,
        "surah_name": video.surah_name,
        "text_arab": video.text_arab,
        "text_translation": video.text_translation,
        "qari": video.qari,
        "background_file": video.background_file,
        "output_file": video.output_file,
        "duration": video.duration,
        "file_size": video.file_size,
        "status": video.status,
        "created_at": video.created_at.isoformat() if video.created_at else None
    }


@router.get("/{video_id}/download")
async def download_video(video_id: str, db: Session = Depends(get_db)):
    """Download video file"""
    repo = VideoRepository(db)
    video = repo.get_by_id(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if not video.output_file or not os.path.exists(video.output_file):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        video.output_file,
        media_type="video/mp4",
        filename=f"quran_{video.surah_name}_{video.ayat}.mp4"
    )


@router.delete("/{video_id}")
async def delete_video(video_id: str, db: Session = Depends(get_db)):
    """Delete a video"""
    repo = VideoRepository(db)
    
    if not repo.get_by_id(video_id):
        raise HTTPException(status_code=404, detail="Video not found")
    
    repo.delete(video_id)
    return {"status": "deleted", "id": video_id}
