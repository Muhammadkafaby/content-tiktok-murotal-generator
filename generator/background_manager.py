import os
import random
import httpx
import uuid
from pathlib import Path
from typing import List, Optional
from api.config import BACKGROUNDS_DIR


class BackgroundManager:
    SUPPORTED_FORMATS = [".mp4", ".mov", ".avi", ".webm"]
    PEXELS_API_URL = "https://api.pexels.com/videos/search"
    
    # Search queries for Islamic/nature backgrounds
    SEARCH_QUERIES = [
        "nature landscape",
        "ocean waves",
        "clouds sky",
        "forest trees",
        "mountains",
        "sunset",
        "stars night sky",
        "rain drops",
        "waterfall",
        "desert sand"
    ]
    
    def __init__(self, backgrounds_dir: Path = BACKGROUNDS_DIR):
        self.backgrounds_dir = backgrounds_dir
        self._cache: List[str] = []
        self.pexels_api_key = os.getenv("PEXELS_API_KEY", "")
    
    def scan_backgrounds(self) -> List[str]:
        """Scan and cache available background videos"""
        self._cache = []
        
        if not self.backgrounds_dir.exists():
            self.backgrounds_dir.mkdir(parents=True, exist_ok=True)
            return self._cache
        
        for file in self.backgrounds_dir.iterdir():
            if file.suffix.lower() in self.SUPPORTED_FORMATS:
                self._cache.append(str(file))
        
        return self._cache
    
    def get_backgrounds(self) -> List[str]:
        """Get list of available backgrounds"""
        if not self._cache:
            self.scan_backgrounds()
        return self._cache
    
    def get_random_background(self) -> Optional[str]:
        """Get random background video path"""
        backgrounds = self.get_backgrounds()
        if not backgrounds:
            return None
        return random.choice(backgrounds)

    
    async def download_from_pexels(self, query: str = None) -> Optional[str]:
        """Download a random video from Pexels API"""
        if not self.pexels_api_key:
            print("PEXELS_API_KEY not set")
            return None
        
        if query is None:
            query = random.choice(self.SEARCH_QUERIES)
        
        try:
            async with httpx.AsyncClient() as client:
                # Search for videos
                response = await client.get(
                    self.PEXELS_API_URL,
                    headers={"Authorization": self.pexels_api_key},
                    params={
                        "query": query,
                        "orientation": "portrait",
                        "size": "medium",
                        "per_page": 15
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    print(f"Pexels API error: {response.status_code}")
                    return None
                
                data = response.json()
                videos = data.get("videos", [])
                
                if not videos:
                    print(f"No videos found for query: {query}")
                    return None
                
                # Pick a random video
                video = random.choice(videos)
                video_files = video.get("video_files", [])
                
                # Find HD quality video (720p or 1080p)
                video_url = None
                for vf in video_files:
                    if vf.get("quality") in ["hd", "sd"] and vf.get("height", 0) >= 720:
                        video_url = vf.get("link")
                        break
                
                if not video_url and video_files:
                    video_url = video_files[0].get("link")
                
                if not video_url:
                    return None
                
                # Download the video
                filename = f"pexels_{video.get('id')}_{uuid.uuid4().hex[:6]}.mp4"
                filepath = self.backgrounds_dir / filename
                
                print(f"Downloading background from Pexels: {query}")
                video_response = await client.get(video_url, timeout=120.0)
                
                if video_response.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(video_response.content)
                    
                    # Add to cache
                    self._cache.append(str(filepath))
                    print(f"Downloaded: {filename}")
                    return str(filepath)
                
        except Exception as e:
            print(f"Error downloading from Pexels: {e}")
        
        return None
    
    async def get_or_download_background(self) -> Optional[str]:
        """Get existing background or download new one from Pexels"""
        # First try to get existing background
        background = self.get_random_background()
        
        if background:
            return background
        
        # If no backgrounds, try to download from Pexels
        print("No local backgrounds found, downloading from Pexels...")
        return await self.download_from_pexels()
    
    def background_exists(self, filename: str) -> bool:
        """Check if background file exists"""
        return filename in self.get_backgrounds()
    
    def get_background_count(self) -> int:
        """Get total number of backgrounds"""
        return len(self.get_backgrounds())
