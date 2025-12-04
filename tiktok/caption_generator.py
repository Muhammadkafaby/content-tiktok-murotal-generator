from typing import Dict, Any, Optional
import random


class CaptionGenerator:
    DEFAULT_HASHTAGS = "#quran #murotal #islamic #muslim #ayatquran #dakwah #islam #fyp #quranquotes #reminder"
    
    # Emotional intro templates based on theme
    INTRO_TEMPLATES = {
        "warning": [
            "⚠️ Ayat ini mengingatkan kita...",
            "🔥 Peringatan penting dari Allah SWT:",
            "❗ Jangan abaikan firman ini:",
        ],
        "promise": [
            "✨ Kabar gembira dari Allah SWT!",
            "🌟 Janji indah untuk orang beriman:",
            "💫 SubhanAllah, Allah menjanjikan:",
        ],
        "guidance": [
            "📖 Petunjuk hidup dari Al-Quran:",
            "🧭 Allah menunjukkan jalan yang benar:",
            "💡 Hikmah yang luar biasa:",
        ],
        "reminder": [
            "💭 Renungkan ayat ini dalam-dalam...",
            "⏰ Pengingat untuk kita semua:",
            "📌 Jangan pernah lupa hal ini:",
        ],
        "mercy": [
            "💝 Kasih sayang Allah tak terbatas:",
            "🤲 Allah Maha Pengampun, jangan putus asa!",
            "❤️ Rahmat Allah meliputi segalanya:",
        ],
        "general": [
            "📖 Ayat yang menyentuh hati:",
            "✨ Keindahan Al-Quran:",
            "🕌 Firman Allah yang penuh makna:",
        ]
    }
    
    # Emotional closing templates
    CLOSING_TEMPLATES = [
        "\n\n🤲 Semoga kita termasuk hamba yang mengamalkannya.",
        "\n\n💫 Tag temanmu yang butuh pengingat ini!",
        "\n\n❤️ Like & share jika bermanfaat!",
        "\n\n🌙 Jadikan ini pengingat harianmu.",
        "\n\n✨ Simpan video ini untuk dibaca lagi.",
        "\n\n🤲 Aamiin ya Rabbal 'Alamin.",
    ]
    
    # Theme keywords for detection
    THEME_KEYWORDS = {
        "warning": ["azab", "neraka", "siksa", "celaka", "binasa", "hukuman", "murka", "zalim", "kafir", "dosa"],
        "promise": ["surga", "pahala", "balasan", "nikmat", "kebahagiaan", "beruntung", "menang", "selamat", "ridha"],
        "guidance": ["petunjuk", "jalan", "benar", "lurus", "perintah", "larangan", "hukum", "syariat"],
        "reminder": ["ingat", "lupa", "lalai", "akhirat", "mati", "kiamat", "hisab"],
        "mercy": ["ampun", "rahmat", "kasih", "sayang", "taubat", "maaf", "pengampun"],
    }
    
    def __init__(self):
        pass
    
    def _detect_theme(self, translation: str) -> str:
        """Detect theme from translation text"""
        translation_lower = translation.lower()
        
        theme_scores = {}
        for theme, keywords in self.THEME_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in translation_lower)
            if score > 0:
                theme_scores[theme] = score
        
        if theme_scores:
            return max(theme_scores, key=theme_scores.get)
        return "general"
    
    def generate_template_caption(
        self,
        surah_name: str,
        ayat_number: int,
        translation: str,
        hashtags: str = None
    ) -> str:
        """Generate emotional caption using template"""
        if hashtags is None:
            hashtags = self.DEFAULT_HASHTAGS
        
        # Detect theme
        theme = self._detect_theme(translation)
        
        # Get intro based on theme
        intros = self.INTRO_TEMPLATES.get(theme, self.INTRO_TEMPLATES["general"])
        intro = random.choice(intros)
        
        # Get random closing
        closing = random.choice(self.CLOSING_TEMPLATES)
        
        # Build caption
        caption = f"""{intro}

📜 QS. {surah_name}: {ayat_number}

"{translation}"
{closing}

👆 Follow untuk ayat harian lainnya!

{hashtags}"""
        
        return caption
    
    def generate_caption(
        self,
        surah_name: str,
        ayat_number: int,
        text_translation: str,
        hashtags: str = None
    ) -> str:
        """Generate caption (sync version)"""
        return self.generate_template_caption(
            surah_name, ayat_number, text_translation, hashtags
        )
