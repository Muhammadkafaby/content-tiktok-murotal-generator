from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from api.models.video import Video
import os


class VideoRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, video_data: dict) -> Video:
        """Create a new video record"""
        video = Video(**video_data)
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        return video
    
    def get_by_id(self, video_id: str) -> Optional[Video]:
        """Get video by ID"""
        return self.db.query(Video).filter(Video.id == video_id).first()
    
    def get_all(self, page: int = 1, limit: int = 10) -> Tuple[List[Video], int]:
        """Get all videos with pagination"""
        offset = (page - 1) * limit
        total = self.db.query(Video).count()
        videos = self.db.query(Video)\
            .order_by(desc(Video.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()
        return videos, total
    
    def get_by_status(self, status: str) -> List[Video]:
        """Get videos by status"""
        return self.db.query(Video).filter(Video.status == status).all()
    
    def get_used_ayat(self) -> set:
        """Get set of (surah, ayat) tuples that have been used"""
        videos = self.db.query(Video.surah, Video.ayat).all()
        return {(v.surah, v.ayat) for v in videos}
    
    def update(self, video_id: str, update_data: dict) -> Optional[Video]:
        """Update video record"""
        video = self.get_by_id(video_id)
        if video:
            for key, value in update_data.items():
                setattr(video, key, value)
            self.db.commit()
            self.db.refresh(video)
        return video
    
    def update_status(self, video_id: str, status: str) -> Optional[Video]:
        """Update video status"""
        return self.update(video_id, {"status": status})
    
    def delete(self, video_id: str) -> bool:
        """Delete video record and file"""
        video = self.get_by_id(video_id)
        if video:
            # Delete file if exists
            if video.output_file and os.path.exists(video.output_file):
                os.remove(video.output_file)
            self.db.delete(video)
            self.db.commit()
            return True
        return False
    
    def count(self) -> int:
        """Get total video count"""
        return self.db.query(Video).count()
    
    def count_by_status(self, status: str) -> int:
        """Get video count by status"""
        return self.db.query(Video).filter(Video.status == status).count()
    
    def get_total_size(self) -> int:
        """Get total size of all videos in bytes"""
        from sqlalchemy import func
        result = self.db.query(func.sum(Video.file_size)).scalar()
        return result or 0
