from typing import Dict, Any, Optional
import random
import urllib.parse
import httpx


class CaptionGenerator:
    DEFAULT_HASHTAGS = "#quran #murotal #islamic #muslim #ayatquran #dakwah #islam #fyp #quranquotes #reminder"
    
    def __init__(self):
        self.ai_api_url = "https://api.elrayyxml.web.id/api/ai/chatgpt"
        
        # Fallback templates jika AI gagal
        self.fallback_intros = [
            "Ayat ini menyentuh hati...",
            "Renungkan firman Allah ini...",
            "Pesan penting dari Al-Quran:",
        ]
        self.fallback_closings = [
            "Semoga bermanfaat.",
            "Simpan dan bagikan.",
            "Follow untuk ayat lainnya.",
        ]
    
    def _generate_with_ai(self, surah_name: str, ayat_number: int, translation: str) -> Optional[str]:
        """Generate caption using AI API"""
        
        prompt = f"""Buatkan caption TikTok untuk video ayat Al-Quran berikut:

Surah: {surah_name}
Ayat: {ayat_number}
Terjemahan: "{translation}"

ATURAN PENTING:
1. Bahasa Indonesia yang PERSONAL dan EMOSIONAL
2. Tone: hangat, menyentuh hati, tidak kaku/formal
3. Mulai dengan kalimat pembuka yang engaging (tanpa emoji berlebihan)
4. Sertakan kutipan ayat dengan format: QS. {surah_name}: {ayat_number}
5. Akhiri dengan ajakan follow yang natural
6. Maksimal 200 kata
7. Gunakan emoji secukupnya (1-3 saja)
8. Buat seperti curhat ke teman, bukan ceramah

CONTOH GAYA YANG DIINGINKAN:
"Pernah nggak sih merasa jauh dari Allah? Ayat ini kayak pelukan hangat buat hati yang lelah...

QS. Al-Baqarah: 186

'Dan apabila hamba-hamba-Ku bertanya kepadamu tentang Aku, maka sesungguhnya Aku dekat.'

Allah itu dekat. Lebih dekat dari yang kita kira. Tinggal kita mau nggak mendekat ke-Nya.

Simpan buat pengingat ya. Follow buat ayat harian."

Tulis caption-nya:"""

        try:
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"{self.ai_api_url}?text={encoded_prompt}"
            
            response = httpx.get(url, timeout=15.0)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("result"):
                    caption = data["result"].strip()
                    # Add hashtags if not present
                    if "#" not in caption:
                        caption += f"\n\n{self.DEFAULT_HASHTAGS}"
                    return caption
            return None
        except Exception as e:
            print(f"AI caption generation failed: {e}")
            return None
    
    def _generate_fallback_caption(
        self,
        surah_name: str,
        ayat_number: int,
        translation: str,
        hashtags: str = None
    ) -> str:
        """Generate fallback caption if AI fails"""
        if hashtags is None:
            hashtags = self.DEFAULT_HASHTAGS
        
        intro = random.choice(self.fallback_intros)
        closing = random.choice(self.fallback_closings)
        
        caption = f"""{intro}

QS. {surah_name}: {ayat_number}

"{translation}"

{closing}

Follow untuk ayat harian lainnya.

{hashtags}"""
        
        return caption
    
    def generate_caption(
        self,
        surah_name: str,
        ayat_number: int,
        text_translation: str,
        hashtags: str = None
    ) -> str:
        """Generate caption - try AI first, fallback to template"""
        
        # Try AI generation
        ai_caption = self._generate_with_ai(surah_name, ayat_number, text_translation)
        if ai_caption:
            # Ensure hashtags are included
            if hashtags and hashtags not in ai_caption:
                ai_caption += f"\n\n{hashtags}"
            elif not hashtags and self.DEFAULT_HASHTAGS not in ai_caption:
                ai_caption += f"\n\n{self.DEFAULT_HASHTAGS}"
            return ai_caption
        
        # Fallback to template
        return self._generate_fallback_caption(
            surah_name, ayat_number, text_translation, hashtags
        )
    
    # Alias for backward compatibility
    def generate_template_caption(
        self,
        surah_name: str,
        ayat_number: int,
        translation: str,
        hashtags: str = None
    ) -> str:
        """Alias for generate_caption"""
        return self.generate_caption(surah_name, ayat_number, translation, hashtags)
