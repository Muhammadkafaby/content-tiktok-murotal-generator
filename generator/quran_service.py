import httpx
from typing import Optional, Dict, Any
from api.config import QURAN_API_BASE, QARI_OPTIONS

# Total ayat per surah
AYAT_PER_SURAH = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109,
    123, 111, 43, 52, 99, 128, 111, 110, 98, 135,
    112, 78, 118, 64, 77, 227, 93, 88, 69, 60,
    34, 30, 73, 54, 45, 83, 182, 88, 75, 85,
    54, 53, 89, 59, 37, 35, 38, 29, 18, 45,
    60, 49, 62, 55, 78, 96, 29, 22, 24, 13,
    14, 11, 11, 18, 12, 12, 30, 52, 52, 44,
    28, 28, 20, 56, 40, 31, 50, 40, 46, 42,
    29, 19, 36, 25, 22, 17, 19, 26, 30, 20,
    15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
    11, 8, 3, 9, 5, 4, 7, 3, 6, 3,
    5, 4, 5, 6
]

TOTAL_AYAT = sum(AYAT_PER_SURAH)  # 6236


class QuranService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_ayat(self, surah: int, ayat: int, qari: str = "alafasy") -> Dict[str, Any]:
        """Fetch ayat data including text and audio"""
        qari_code = QARI_OPTIONS.get(qari, "ar.alafasy")
        
        # Get Arabic text with audio
        audio_url = f"{QURAN_API_BASE}/ayah/{surah}:{ayat}/{qari_code}"
        audio_response = await self.client.get(audio_url)
        audio_data = audio_response.json()
        
        # Get Indonesian translation
        trans_url = f"{QURAN_API_BASE}/ayah/{surah}:{ayat}/id.indonesian"
        trans_response = await self.client.get(trans_url)
        trans_data = trans_response.json()
        
        if audio_data.get("code") != 200 or trans_data.get("code") != 200:
            raise Exception(f"Failed to fetch ayat {surah}:{ayat}")
        
        return {
            "surah": surah,
            "ayat": ayat,
            "surah_name": audio_data["data"]["surah"]["englishName"],
            "surah_name_arabic": audio_data["data"]["surah"]["name"],
            "text_arab": audio_data["data"]["text"],
            "text_translation": trans_data["data"]["text"],
            "audio_url": audio_data["data"]["audio"],
            "qari": qari
        }
    
    async def download_audio(self, audio_url: str, output_path: str) -> str:
        """Download audio file"""
        response = await self.client.get(audio_url)
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    
    def get_random_ayat_reference(self, used_ayat: set = None) -> tuple[int, int]:
        """Get random surah:ayat that hasn't been used"""
        import random
        
        if used_ayat is None:
            used_ayat = set()
        
        available = []
        for surah_idx, ayat_count in enumerate(AYAT_PER_SURAH, start=1):
            for ayat in range(1, ayat_count + 1):
                ref = (surah_idx, ayat)
                if ref not in used_ayat:
                    available.append(ref)
        
        if not available:
            raise Exception("All ayat have been used")
        
        return random.choice(available)
    
    def is_valid_ayat(self, surah: int, ayat: int) -> bool:
        """Check if surah:ayat is valid"""
        if surah < 1 or surah > 114:
            return False
        if ayat < 1 or ayat > AYAT_PER_SURAH[surah - 1]:
            return False
        return True
    
    async def close(self):
        await self.client.aclose()
