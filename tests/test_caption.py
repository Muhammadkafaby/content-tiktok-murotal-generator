"""
Property tests for caption generator
**Feature: quran-video-generator, Property 16: Caption Generation**
**Feature: quran-video-generator, Property 18: AI Caption Content Validity**
**Validates: Requirements 6.3, 7.2**
"""
import pytest
from hypothesis import given, strategies as st, settings
from tiktok.caption_generator import CaptionGenerator


class TestCaptionGeneration:
    """
    Property 16: Caption Generation
    For any TikTok post, the caption SHALL contain the surah name, ayat number,
    translation text, and configured hashtags.
    """
    
    @given(
        surah_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L',))),
        ayat_number=st.integers(min_value=1, max_value=286),
        translation=st.text(min_size=1, max_size=300)
    )
    @settings(max_examples=30)
    def test_template_caption_contains_required_elements(self, surah_name, ayat_number, translation):
        """Template caption should contain surah name, ayat number, and translation"""
        generator = CaptionGenerator()
        
        caption = generator.generate_template_caption(
            surah_name=surah_name,
            ayat_number=ayat_number,
            translation=translation
        )
        
        # Should contain surah name
        assert surah_name in caption
        
        # Should contain ayat number
        assert str(ayat_number) in caption
        
        # Should contain translation
        assert translation in caption
        
        # Should contain default hashtags
        assert "#quran" in caption
        assert "#murotal" in caption
    
    @given(
        surah_name=st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('L',))),
        ayat_number=st.integers(min_value=1, max_value=286),
        translation=st.text(min_size=1, max_size=200),
        custom_hashtags=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=20)
    def test_custom_hashtags_included(self, surah_name, ayat_number, translation, custom_hashtags):
        """Custom hashtags should be included in caption"""
        generator = CaptionGenerator()
        
        caption = generator.generate_template_caption(
            surah_name=surah_name,
            ayat_number=ayat_number,
            translation=translation,
            hashtags=custom_hashtags
        )
        
        assert custom_hashtags in caption


class TestAICaptionContentValidity:
    """
    Property 18: AI Caption Content Validity
    For any AI-generated caption, the output SHALL contain the surah name,
    ayat number, and relevant Islamic hashtags.
    """
    
    def test_fallback_to_template_without_api_key(self):
        """Without API key, should fallback to template"""
        generator = CaptionGenerator()
        generator.openai_key = ""  # No API key
        
        # This should use template fallback
        import asyncio
        caption = asyncio.get_event_loop().run_until_complete(
            generator.generate_ai_caption(
                surah_name="Al-Fatiha",
                ayat_number=1,
                text_arab="بِسْمِ اللَّهِ",
                translation="Dengan nama Allah"
            )
        )
        
        # Should still contain required elements (from template fallback)
        assert "Al-Fatiha" in caption
        assert "1" in caption
        assert "Dengan nama Allah" in caption
    
    @given(mode=st.sampled_from(["template", "ai"]))
    @settings(max_examples=10)
    def test_generate_caption_mode_selection(self, mode):
        """Caption generation should respect mode selection"""
        generator = CaptionGenerator()
        generator.openai_key = ""  # Force template fallback for AI mode
        
        import asyncio
        caption = asyncio.get_event_loop().run_until_complete(
            generator.generate_caption(
                mode=mode,
                surah_name="Al-Baqarah",
                ayat_number=255,
                text_arab="اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ",
                translation="Allah, tidak ada tuhan selain Dia"
            )
        )
        
        # Both modes should produce valid caption with required elements
        assert "Al-Baqarah" in caption
        assert "255" in caption
    
    def test_default_hashtags_are_islamic(self):
        """Default hashtags should be Islamic-related"""
        generator = CaptionGenerator()
        
        hashtags = generator.DEFAULT_HASHTAGS
        
        # Should contain Islamic hashtags
        assert "#quran" in hashtags.lower()
        assert "#islamic" in hashtags.lower() or "#islam" in hashtags.lower()
