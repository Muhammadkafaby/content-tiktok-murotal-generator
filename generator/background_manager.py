import os
import random
from pathlib import Path
from typing import List, Optional
from api.config import BACKGROUNDS_DIR


class BackgroundManager:
    SUPPORTED_FORMATS = [".mp4", ".mov", ".avi", ".webm"]
    
    def __init__(self, backgrounds_dir: Path = BACKGROUNDS_DIR):
        self.backgrounds_dir = backgrounds_dir
        self._cache: List[str] = []
    
    def scan_backgrounds(self) -> List[str]:
        """Scan and cache available background videos"""
        self._cache = []
        
        if not self.backgrounds_dir.exists():
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
    
    def background_exists(self, filename: str) -> bool:
        """Check if background file exists"""
        return filename in self.get_backgrounds()
    
    def get_background_count(self) -> int:
        """Get total number of backgrounds"""
        return len(self.get_backgrounds())
