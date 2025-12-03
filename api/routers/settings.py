from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from api.database import get_db
from api.repositories.settings_repository import SettingsRepository

router = APIRouter()


class SettingsUpdate(BaseModel):
    qari: Optional[str] = None
    schedule_enabled: Optional[bool] = None
    schedule_time: Optional[str] = None
    videos_per_day: Optional[int] = None
    tiktok_auto_post: Optional[bool] = None
    tiktok_post_delay: Optional[int] = None
    tiktok_hashtags: Optional[str] = None
    caption_mode: Optional[str] = None


@router.get("")
async def get_settings(db: Session = Depends(get_db)):
    """Get current settings"""
    repo = SettingsRepository(db)
    settings = repo.get()
    return repo.to_dict(settings)


@router.put("")
async def update_settings(settings: SettingsUpdate, db: Session = Depends(get_db)):
    """Update settings"""
    repo = SettingsRepository(db)
    updated = repo.update(settings.model_dump(exclude_none=True))
    return {"status": "updated", "settings": repo.to_dict(updated)}
