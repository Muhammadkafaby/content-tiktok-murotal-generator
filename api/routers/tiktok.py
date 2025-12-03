from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class TikTokSettings(BaseModel):
    auto_post: Optional[bool] = None
    post_delay: Optional[int] = None


@router.post("/login")
async def initiate_login():
    """Initiate TikTok login flow"""
    # TODO: Implement with Playwright
    return {"status": "login_required", "message": "Please complete login in browser"}


@router.get("/status")
async def get_tiktok_status():
    """Check TikTok login status"""
    # TODO: Implement with session repository
    return {"logged_in": False, "username": None}


@router.post("/post/{video_id}")
async def post_to_tiktok(video_id: str):
    """Manually post a video to TikTok"""
    # TODO: Implement with TikTok service
    raise HTTPException(status_code=400, detail="TikTok not logged in")


@router.get("/history")
async def get_posting_history(limit: int = 20):
    """Get TikTok posting history"""
    # TODO: Implement with repository
    return {"history": [], "total": 0}


@router.put("/settings")
async def update_tiktok_settings(settings: TikTokSettings):
    """Update TikTok auto-post settings"""
    # TODO: Implement with repository
    return {"status": "updated"}
