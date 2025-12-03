from typing import Dict, Any, Optional
import httpx
import urllib.parse


class CaptionGenerator:
    DEFAULT_HASHTAGS = "#quran #murotal #islamic #muslim #ayatquran #dakwah #islam #fyp"
    AI_API_URL = "https://api.elrayyxml.web.id/api/ai/chatgpt"
    
    def __init__(self):
        pass
    
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
        """Generate caption using free AI API (elrayyxml)"""
        if hashtags is None:
            hashtags = self.DEFAULT_HASHTAGS
        
        prompt = f"""Buatkan caption TikTok yang engaging untuk video quotes Al-Quran:

Surah: {surah_name}
Ayat: {ayat_number}
Terjemahan: {translation}

Instruksi:
1. Buat caption menarik dan inspiratif dalam Bahasa Indonesia
2. Sertakan emoji yang relevan
3. Tambahkan hikmah singkat dari ayat tersebut
4. Maksimal 150 kata
5. Akhiri dengan hashtag: {hashtags}"""

        try:
            # URL encode the prompt
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"{self.AI_API_URL}?text={encoded_prompt}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                
                if response.status_code == 200:
                    # API returns plain text response
                    caption = response.text.strip()
                    if caption and len(caption) > 10:
                        return caption
                
        except Exception as e:
            # Fallback to template on error
            pass
        
        return self.generate_template_caption(surah_name, ayat_number, translation, hashtags)
    
    def generate_caption(
        self,
        surah_name: str,
        ayat_number: int,
        text_translation: str,
        hashtags: str = None
    ) -> str:
        """Generate caption (sync version for simple use)"""
        return self.generate_template_caption(
            surah_name, ayat_number, text_translation, hashtags
        )
    
    async def generate_caption_async(
        self,
        mode: str,
        surah_name: str,
        ayat_number: int,
        text_arab: str,
        translation: str,
        hashtags: str = None
    ) -> str:
        """Generate caption based on mode (async)"""
        if mode == "ai":
            return await self.generate_ai_caption(
                surah_name, ayat_number, text_arab, translation, hashtags
            )
        else:
            return self.generate_template_caption(
                surah_name, ayat_number, translation, hashtags
            )
