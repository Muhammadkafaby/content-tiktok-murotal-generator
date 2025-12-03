import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page
from api.config import SESSIONS_DIR


class TikTokUploader:
    TIKTOK_UPLOAD_URL = "https://www.tiktok.com/upload"
    COOKIES_FILE = SESSIONS_DIR / "tiktok_cookies.json"
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def init_browser(self, headless: bool = True):
        """Initialize Playwright browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=headless)
        self.page = await self.browser.new_page()
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
    
    async def load_cookies(self) -> bool:
        """Load saved session cookies"""
        if not self.COOKIES_FILE.exists():
            return False
        
        try:
            with open(self.COOKIES_FILE, 'r') as f:
                cookies = json.load(f)
            await self.page.context.add_cookies(cookies)
            return True
        except Exception:
            return False
    
    async def save_cookies(self):
        """Save current session cookies"""
        cookies = await self.page.context.cookies()
        with open(self.COOKIES_FILE, 'w') as f:
            json.dump(cookies, f)
    
    async def is_logged_in(self) -> bool:
        """Check if currently logged in to TikTok"""
        await self.page.goto("https://www.tiktok.com")
        await asyncio.sleep(2)
        
        # Check for login indicators
        try:
            await self.page.wait_for_selector('[data-e2e="profile-icon"]', timeout=5000)
            return True
        except Exception:
            return False
    
    async def login_manual(self) -> Dict[str, Any]:
        """Initiate manual login flow"""
        await self.page.goto("https://www.tiktok.com/login")
        
        return {
            "status": "waiting_login",
            "message": "Please complete login in the browser window"
        }
    
    async def upload_video(
        self,
        video_path: str,
        caption: str,
        hashtags: str = ""
    ) -> Dict[str, Any]:
        """Upload video to TikTok"""
        try:
            # Navigate to upload page
            await self.page.goto(self.TIKTOK_UPLOAD_URL)
            await asyncio.sleep(3)
            
            # Upload file
            file_input = await self.page.query_selector('input[type="file"]')
            if file_input:
                await file_input.set_input_files(video_path)
                await asyncio.sleep(5)  # Wait for upload
            
            # Fill caption
            full_caption = f"{caption}\n\n{hashtags}".strip()
            caption_input = await self.page.query_selector('[data-e2e="caption-input"]')
            if caption_input:
                await caption_input.fill(full_caption)
            
            # Click post button
            post_button = await self.page.query_selector('[data-e2e="post-button"]')
            if post_button:
                await post_button.click()
                await asyncio.sleep(10)  # Wait for posting
            
            return {
                "status": "success",
                "message": "Video posted successfully"
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def get_username(self) -> Optional[str]:
        """Get logged in username"""
        try:
            await self.page.goto("https://www.tiktok.com")
            profile_link = await self.page.query_selector('[data-e2e="profile-icon"]')
            if profile_link:
                href = await profile_link.get_attribute('href')
                if href:
                    return href.split('/')[-1].replace('@', '')
        except Exception:
            pass
        return None
