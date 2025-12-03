from typing import Optional
from sqlalchemy.orm import Session
from api.models.settings import Settings


class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get(self) -> Settings:
        """Get settings (create default if not exists)"""
        settings = self.db.query(Settings).first()
        if not settings:
            settings = Settings(id=1)
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        return settings
    
    def update(self, update_data: dict) -> Settings:
        """Update settings"""
        settings = self.get()
        for key, value in update_data.items():
            if value is not None and hasattr(settings, key):
                setattr(settings, key, value)
        self.db.commit()
        self.db.refresh(settings)
        return settings
    
    def to_dict(self, settings: Settings) -> dict:
        """Convert settings to dictionary"""
        return {
            "qari": settings.qari,
            "schedule_enabled": settings.schedule_enabled,
            "schedule_time": settings.schedule_time,
            "videos_per_day": settings.videos_per_day,
            "max_ayat_length": settings.max_ayat_length,
            "tiktok_auto_post": settings.tiktok_auto_post,
            "tiktok_post_delay": settings.tiktok_post_delay,
            "tiktok_hashtags": settings.tiktok_hashtags,
            "caption_mode": settings.caption_mode
        }
