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
        # Quran.com API for word timestamps
        self.quran_com_api = "https://api.quran.com/api/v4"
        # Recitation IDs for different qaris on Quran.com
        self.recitation_ids = {
            "alafasy": 7,      # Mishary Rashid Alafasy
            "abdulbasit": 1,   # Abdul Basit (Murattal)
            "sudais": 6,       # Abdurrahman As-Sudais
            "husary": 5,       # Mahmoud Khalil Al-Husary
            "minshawi": 4,     # Mohamed Siddiq El-Minshawi
        }
    
    async def get_word_timestamps(self, surah: int, ayat: int, qari: str = "alafasy") -> dict:
        """
        Fetch word-level timestamps and audio URL from Quran.com API.
        
        Returns dict with:
        - word_timings: list of timing dicts
        - audio_url: URL to the audio file (for sync)
        """
        recitation_id = self.recitation_ids.get(qari, 7)
        
        try:
            # Get verse key (e.g., "2:255" for Ayatul Kursi)
            verse_key = f"{surah}:{ayat}"
            
            # Fetch timestamps from Quran.com
            url = f"{self.quran_com_api}/recitations/{recitation_id}/by_ayah/{verse_key}"
            response = await self.client.get(url)
            
            if response.status_code != 200:
                return {"word_timings": [], "audio_url": None}
            
            data = response.json()
            
            # Extract word timings and audio URL
            word_timings = []
            audio_url = None
            
            if "audio_files" in data and data["audio_files"]:
                audio_file = data["audio_files"][0]
                
                # Get audio URL from Quran.com (this is synced with timestamps)
                if "url" in audio_file:
                    audio_url = audio_file["url"]
                    # Quran.com uses relative URLs, prepend base
                    if audio_url and not audio_url.startswith("http"):
                        audio_url = f"https://verses.quran.com/{audio_url}"
                
                if "segments" in audio_file:
                    for segment in audio_file["segments"]:
                        # segment format: [word_position, start_ms, end_ms]
                        if len(segment) >= 3:
                            word_timings.append({
                                "position": segment[0],
                                "start_ms": segment[1],
                                "end_ms": segment[2]
                            })
            
            return {"word_timings": word_timings, "audio_url": audio_url}
            
        except Exception as e:
            print(f"Error fetching word timestamps: {e}")
            return {"word_timings": [], "audio_url": None}
    
    async def get_ayat_with_timestamps(self, surah: int, ayat: int, qari: str = "alafasy") -> Dict[str, Any]:
        """Fetch ayat data including text, audio, and word timestamps"""
        # Get basic ayat data
        ayat_data = await self.get_ayat(surah, ayat, qari)
        
        # Get word timestamps and synced audio from Quran.com
        timestamp_data = await self.get_word_timestamps(surah, ayat, qari)
        
        # Add timestamps to response
        ayat_data["word_timings"] = timestamp_data["word_timings"]
        
        # Use Quran.com audio if available (synced with timestamps)
        # Otherwise fallback to alquran.cloud audio
        if timestamp_data["audio_url"]:
            ayat_data["audio_url"] = timestamp_data["audio_url"]
            print(f"Using Quran.com synced audio: {timestamp_data['audio_url']}")
        
        return ayat_data
    
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
