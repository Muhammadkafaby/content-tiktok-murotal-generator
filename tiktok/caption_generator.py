from typing import Dict, Any, Optional
import httpx
from api.config import OPENAI_API_KEY


class CaptionGenerator:
    DEFAULT_HASHTAGS = "#quran #murotal #islamic #muslim #ayatquran #dakwah #islam #fyp"
    
    def __init__(self):
        self.openai_key = OPENAI_API_KEY
    
    def generate_template_caption(
        self,
        surah_name: str,
        ayat_number: int,
        translation: str,
        hashtags: str = None
    ) -> str:
        """Generate caption using template"""
        if hashtags is None:
            hashtags = self.DEFAULT_HASHTAGS
        
        return f"""{surah_name} - Ayat {ayat_number}

{translation}

{hashtags}"""
    
    async def generate_ai_caption(
        self,
        surah_name: str,
        ayat_number: int,
        text_arab: str,
        translation: str,
        hashtags: str = None
    ) -> str:
        """Generate caption using OpenAI API"""
        if not self.openai_key:
            # Fallback to template if no API key
            return self.generate_template_caption(surah_name, ayat_number, translation, hashtags)
        
        if hashtags is None:
            hashtags = self.DEFAULT_HASHTAGS
        
        prompt = f"""Buatkan caption TikTok yang engaging untuk video quotes Al-Quran dengan informasi berikut:

Surah: {surah_name}
Ayat: {ayat_number}
Teks Arab: {text_arab}
Terjemahan: {translation}

Instruksi:
1. Buat caption yang menarik dan inspiratif dalam Bahasa Indonesia
2. Sertakan emoji yang relevan
3. Tambahkan konteks atau hikmah singkat dari ayat tersebut
4. Jangan terlalu panjang (maksimal 200 kata)
5. Akhiri dengan hashtag: {hashtags}

Format output:
[Emoji pembuka] [Judul menarik]

[Konteks/hikmah singkat]

"{translation}"
- {surah_name}: {ayat_number}

[Pesan penutup dengan emoji]

{hashtags}"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "Kamu adalah content creator Islami yang membuat caption TikTok yang engaging dan inspiratif."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 500,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                
        except Exception as e:
            # Fallback to template on error
            pass
        
        return self.generate_template_caption(surah_name, ayat_number, translation, hashtags)
    
    async def generate_caption(
        self,
        mode: str,
        surah_name: str,
        ayat_number: int,
        text_arab: str,
        translation: str,
        hashtags: str = None
    ) -> str:
        """Generate caption based on mode"""
        if mode == "ai":
            return await self.generate_ai_caption(
                surah_name, ayat_number, text_arab, translation, hashtags
            )
        else:
            return self.generate_template_caption(
                surah_name, ayat_number, translation, hashtags
            )
