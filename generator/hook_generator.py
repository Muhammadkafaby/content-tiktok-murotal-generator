import random
from typing import Optional


class HookGenerator:
    """Generate engaging hooks for video based on ayat content"""
    
    # Template hooks berdasarkan tema ayat
    HOOK_TEMPLATES = {
        "warning": [
            "⚠️ Peringatan keras dari Allah...",
            "🔥 Jangan abaikan ayat ini!",
            "❗ Allah memperingatkan kita...",
            "⛔ Hati-hati dengan ini...",
        ],
        "promise": [
            "✨ Janji Allah untuk orang beriman...",
            "🌟 Kabar gembira untukmu!",
            "💫 Allah menjanjikan ini...",
            "🎁 Hadiah dari Allah...",
        ],
        "guidance": [
            "📖 Petunjuk hidup dari Allah...",
            "🧭 Jalan yang benar adalah...",
            "💡 Allah mengajarkan kita...",
            "🔑 Kunci kebahagiaan...",
        ],
        "reminder": [
            "💭 Sudahkah kamu ingat ini?",
            "🤔 Renungkan ayat ini...",
            "⏰ Pengingat penting!",
            "📌 Jangan lupa hal ini...",
        ],
        "mercy": [
            "💝 Kasih sayang Allah...",
            "🤲 Allah Maha Pengampun...",
            "❤️ Rahmat Allah sangat luas...",
            "🌈 Jangan putus asa!",
        ],
        "creation": [
            "🌍 Keajaiban ciptaan Allah...",
            "✨ Tanda-tanda kebesaran-Nya...",
            "🌙 Pernahkah kamu pikirkan ini?",
            "🔬 Bukti kekuasaan Allah...",
        ],
        "general": [
            "📖 Dengarkan ayat ini...",
            "🕌 Al-Quran berkata...",
            "✨ Ayat yang indah...",
            "💎 Mutiara Al-Quran...",
            "🌟 Simak baik-baik...",
        ]
    }
    
    # Keywords untuk deteksi tema
    THEME_KEYWORDS = {
        "warning": ["azab", "neraka", "siksa", "celaka", "binasa", "hukuman", "murka", "zalim", "kafir", "dosa"],
        "promise": ["surga", "pahala", "balasan", "nikmat", "kebahagiaan", "beruntung", "menang", "selamat"],
        "guidance": ["petunjuk", "jalan", "benar", "lurus", "perintah", "larangan", "hukum", "syariat"],
        "reminder": ["ingat", "lupa", "lalai", "akhirat", "mati", "kiamat", "hisab"],
        "mercy": ["ampun", "rahmat", "kasih", "sayang", "taubat", "maaf", "pengampun"],
        "creation": ["langit", "bumi", "ciptakan", "mencipta", "tanda", "alam", "matahari", "bulan", "bintang"],
    }
    
    def detect_theme(self, translation: str) -> str:
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
    
    def generate_hook(self, translation: str, surah_name: str = None) -> str:
        """Generate hook text based on ayat translation"""
        theme = self.detect_theme(translation)
        hooks = self.HOOK_TEMPLATES.get(theme, self.HOOK_TEMPLATES["general"])
        return random.choice(hooks)
    
    def generate_custom_hook(self, translation: str) -> Optional[str]:
        """Generate more specific hook based on content"""
        translation_lower = translation.lower()
        
        # Specific hooks based on content
        if "orang-orang yang beriman" in translation_lower:
            return "👤 Apakah kamu termasuk?"
        elif "bertakwa" in translation_lower:
            return "🤲 Ciri orang bertakwa..."
        elif "sabar" in translation_lower:
            return "💪 Kunci kesabaran..."
        elif "syukur" in translation_lower:
            return "🙏 Nikmat yang sering dilupakan..."
        elif "doa" in translation_lower or "berdoa" in translation_lower:
            return "🤲 Doa yang dikabulkan..."
        elif "rezeki" in translation_lower:
            return "💰 Rahasia rezeki..."
        elif "ibu" in translation_lower or "orang tua" in translation_lower:
            return "👨‍👩‍👧 Tentang orang tua..."
        elif "mati" in translation_lower or "kematian" in translation_lower:
            return "⏳ Kematian pasti datang..."
        
        return None
    
    def get_hook(self, translation: str, surah_name: str = None) -> str:
        """Get the best hook for the ayat"""
        # Try custom hook first
        custom = self.generate_custom_hook(translation)
        if custom:
            return custom
        
        # Fall back to template hook
        return self.generate_hook(translation, surah_name)
