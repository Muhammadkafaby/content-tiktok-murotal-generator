import random
import urllib.parse
from typing import Optional
import httpx


class HookGenerator:
    """Generate engaging viral hooks for video using AI"""
    
    def __init__(self):
        self.api_url = "https://api.elrayyxml.web.id/api/ai/chatgpt"
        
        # Fallback hooks jika AI tidak tersedia
        self.fallback_hooks = [
            "Ayat ini mungkin pesan untuk kamu hari ini...",
            "Mungkin Allah ingin kamu baca ini...",
            "Jangan skip, ini penting untuk hidup kamu.",
            "Dengarkan baik-baik ayat ini...",
            "Al-Quran punya pesan untukmu...",
        ]
    
    def _generate_with_ai(self, translation: str, surah_name: str) -> Optional[str]:
        """Generate hook using ElrayyXml ChatGPT API"""
        
        prompt = f"""Buatkan 1 hook pembuka video TikTok Islami (1-2 kalimat pendek) yang SANGAT RELEVAN dengan ayat Al-Quran berikut.

Ayat dari Surah {surah_name}:
"{translation}"

ATURAN:
1. Hook HARUS relevan dengan ISI ayat
2. Bahasa Indonesia casual yang menyentuh hati
3. JANGAN pakai emoji
4. Maksimal 15 kata
5. Jangan sebut nama surah

Tulis HANYA hook-nya saja:"""

        try:
            # URL encode the prompt
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"{self.api_url}?text={encoded_prompt}"
            
            response = httpx.get(url, timeout=15.0)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("result"):
                    hook = data["result"].strip()
                    # Clean up hook
                    hook = hook.strip('"\'')
                    # Remove any prefix like "Hook:" or similar
                    if ":" in hook and len(hook.split(":")[0]) < 15:
                        hook = hook.split(":", 1)[1].strip()
                    # Pastikan tidak terlalu panjang
                    if len(hook) <= 120:
                        return hook
            
            return None
            
        except Exception as e:
            print(f"AI hook generation failed: {e}")
            return None
    
    def get_hook(self, translation: str, surah_name: str = None) -> str:
        """Get the best hook for the ayat"""
        # Try AI first
        if surah_name:
            ai_hook = self._generate_with_ai(translation, surah_name)
            if ai_hook:
                return ai_hook
        
        # Fallback to simple keyword matching
        return self._get_fallback_hook(translation)
    
    def _get_fallback_hook(self, translation: str) -> str:
        """Get fallback hook based on keywords"""
        translation_lower = translation.lower()
        
        # Specific keyword matching
        if any(kw in translation_lower for kw in ["azab", "neraka", "siksa", "hukuman"]):
            return "Jangan sampai kamu termasuk golongan ini..."
        elif any(kw in translation_lower for kw in ["sabar", "ujian", "cobaan"]):
            return "Kalau kamu sedang bersabar, ini untukmu..."
        elif any(kw in translation_lower for kw in ["ampun", "taubat", "rahmat"]):
            return "Belum terlambat untuk kembali..."
        elif any(kw in translation_lower for kw in ["surga", "pahala", "balasan"]):
            return "Janji Allah untuk orang yang beriman..."
        elif any(kw in translation_lower for kw in ["mati", "kematian", "akhirat"]):
            return "Kematian pasti datang... sudah siap?"
        elif any(kw in translation_lower for kw in ["doa", "berdoa"]):
            return "Doa yang pasti dikabulkan Allah..."
        elif any(kw in translation_lower for kw in ["rezeki", "nikmat"]):
            return "Rahasia rezeki yang jarang diketahui..."
        elif any(kw in translation_lower for kw in ["takut", "gelisah", "sedih"]):
            return "Kalau hatimu sedang berat, baca ini..."
        elif any(kw in translation_lower for kw in ["syukur", "bersyukur"]):
            return "Nikmat yang sering kita lupakan..."
        elif any(kw in translation_lower for kw in ["orang tua", "ibu", "ayah"]):
            return "Tentang orang tua... jangan skip ini."
        elif any(kw in translation_lower for kw in ["beriman", "bertakwa"]):
            return "Apakah kamu termasuk orang ini?"
        
        # Random fallback
        return random.choice(self.fallback_hooks)
