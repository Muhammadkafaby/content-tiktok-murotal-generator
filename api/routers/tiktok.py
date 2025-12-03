from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import json

from api.database import get_db
from api.repositories.tiktok_repository import TikTokRepository
from api.repositories.video_repository import VideoRepository
from api.config import SESSIONS_DIR
from tiktok.uploader import TikTokUploader
from tiktok.caption_generator import CaptionGenerator

router = APIRouter()

# Global uploader instance
_uploader: Optional[TikTokUploader] = None

COOKIES_FILE = SESSIONS_DIR / "tiktok_cookies.json"


class CookiesInput(BaseModel):
    cookies: str  # JSON string of cookies


async def get_uploader(headless: bool = True) -> TikTokUploader:
    """Get or create TikTok uploader instance"""
    global _uploader
    if _uploader is None:
        _uploader = TikTokUploader()
        await _uploader.init_browser(headless=headless)
        await _uploader.load_cookies()
    return _uploader


@router.post("/login")
async def initiate_login():
    """
    TikTok login info.
    Since we're running in Docker, browser GUI is not available.
    Use /upload-cookies endpoint to upload cookies from your browser.
    """
    return {
        "status": "info",
        "message": "To login to TikTok, please export cookies from your browser and upload them using the 'Upload Cookies' feature.",
        "instructions": [
            "1. Install a browser extension like 'EditThisCookie' or 'Cookie-Editor'",
            "2. Login to TikTok in your browser",
            "3. Export cookies as JSON",
            "4. Upload the cookies file or paste the JSON below"
        ]
    }


@router.post("/upload-cookies")
async def upload_cookies(cookies_input: CookiesInput):
    """Upload TikTok cookies from browser"""
    try:
        # Parse and validate cookies
        cookies = json.loads(cookies_input.cookies)
        
        if not isinstance(cookies, list):
            raise ValueError("Cookies must be a JSON array")
        
        # Save cookies
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        with open(COOKIES_FILE, 'w') as f:
            json.dump(cookies, f)
        
        # Reload uploader with new cookies
        global _uploader
        if _uploader:
            await _uploader.close()
            _uploader = None
        
        uploader = await get_uploader()
        
        # Cookies saved successfully - assume login will work
        # Actual verification will happen when posting
        return {
            "status": "success", 
            "logged_in": True, 
            "username": "TikTok User",
            "message": "Cookies uploaded successfully. Login will be verified when posting."
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/status")
async def get_tiktok_status():
    """Check TikTok login status"""
    try:
        # Simply check if cookies file exists
        if COOKIES_FILE.exists():
            return {"logged_in": True, "username": "TikTok User"}
        return {"logged_in": False, "username": None}
        
    except Exception as e:
        print(f"TikTok status error: {e}")
        return {"logged_in": False, "username": None}


@router.get("/caption/{video_id}")
async def generate_caption(video_id: str, db: Session = Depends(get_db)):
    """Generate TikTok caption for a video"""
    try:
        video_repo = VideoRepository(db)
        video = video_repo.get_by_id(video_id)
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Get hashtags from settings
        from api.repositories.settings_repository import SettingsRepository
        settings_repo = SettingsRepository(db)
        settings = settings_repo.get()
        hashtags = settings.tiktok_hashtags or "#quran #islam #muslim #ayat #alquran #fyp"
        
        # Generate caption
        caption_gen = CaptionGenerator()
        caption = caption_gen.generate_caption(
            surah_name=video.surah_name,
            ayat_number=video.ayat,
            text_translation=video.text_translation,
            hashtags=hashtags
        )
        
        return {
            "caption": caption,
            "surah_name": video.surah_name,
            "ayat": video.ayat,
            "download_url": f"/api/videos/{video_id}/download"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post/{video_id}")
async def post_to_tiktok(video_id: str, db: Session = Depends(get_db)):
    """Manually post a video to TikTok"""
    try:
        uploader = await get_uploader()
        
        # Check login
        if not await uploader.is_logged_in():
            raise HTTPException(status_code=401, detail="TikTok not logged in. Please upload cookies first.")
        
        # Get video
        video_repo = VideoRepository(db)
        video = video_repo.get_by_id(video_id)
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Generate caption
        caption_gen = CaptionGenerator()
        caption = caption_gen.generate_caption(
            surah_name=video.surah_name,
            ayat_number=video.ayat,
            text_translation=video.text_translation
        )
        
        # Get hashtags from settings
        from api.repositories.settings_repository import SettingsRepository
        settings_repo = SettingsRepository(db)
        settings = settings_repo.get()
        hashtags = settings.tiktok_hashtags or "#quran #islam #muslim #ayat #alquran"
        
        # Upload to TikTok
        result = await uploader.upload_video(
            video_path=video.output_file,
            caption=caption,
            hashtags=hashtags
        )
        
        if result["status"] == "success":
            # Update video status
            video_repo.update(video_id, {"tiktok_posted": True})
            
            # Save to history
            tiktok_repo = TikTokRepository(db)
            tiktok_repo.add_post_history(video_id, "success")
            
            return {"status": "success", "message": "Video posted to TikTok"}
        else:
            tiktok_repo = TikTokRepository(db)
            tiktok_repo.add_post_history(video_id, "failed", result.get("error"))
            raise HTTPException(status_code=500, detail=result.get("error", "Upload failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_posting_history(limit: int = 20, db: Session = Depends(get_db)):
    """Get TikTok posting history"""
    tiktok_repo = TikTokRepository(db)
    history = tiktok_repo.get_history(limit)
    return {"history": history, "total": len(history)}


@router.post("/logout")
async def logout_tiktok():
    """Logout from TikTok"""
    global _uploader
    
    try:
        if _uploader:
            await _uploader.close()
            _uploader = None
        
        # Delete cookies file
        if COOKIES_FILE.exists():
            COOKIES_FILE.unlink()
        
        return {"status": "success", "message": "Logged out from TikTok"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
