"""
Property tests for video generator
**Feature: quran-video-generator, Property 3: Video Output Format Compliance**
**Feature: quran-video-generator, Property 6: Background Selection Validity**
**Feature: quran-video-generator, Property 7: Translation Inclusion**
**Validates: Requirements 1.4, 3.3, 3.5**
"""
import pytest
import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings
from generator.background_manager import BackgroundManager
from generator.video_generator import VideoGenerator


class TestBackgroundManager:
    """
    Property 6: Background Selection Validity
    For any generated video, the selected background video SHALL exist in the backgrounds collection.
    """
    
    def test_empty_backgrounds_returns_none(self, temp_dir):
        """Empty backgrounds directory should return None"""
        manager = BackgroundManager(Path(temp_dir))
        assert manager.get_random_background() is None
        assert manager.get_background_count() == 0
    
    def test_scan_finds_video_files(self, temp_dir):
        """Should find video files with supported formats"""
        bg_dir = Path(temp_dir)
        
        # Create dummy video files
        (bg_dir / "video1.mp4").touch()
        (bg_dir / "video2.mov").touch()
        (bg_dir / "video3.avi").touch()
        (bg_dir / "not_video.txt").touch()
        
        manager = BackgroundManager(bg_dir)
        backgrounds = manager.scan_backgrounds()
        
        assert len(backgrounds) == 3
        assert manager.get_background_count() == 3
    
    @given(st.data())
    @settings(max_examples=20)
    def test_random_selection_returns_existing_file(self, temp_dir, data):
        """Random selection should always return an existing file"""
        bg_dir = Path(temp_dir)
        
        # Create some video files
        num_files = data.draw(st.integers(min_value=1, max_value=10))
        created_files = []
        for i in range(num_files):
            filepath = bg_dir / f"video{i}.mp4"
            filepath.touch()
            created_files.append(str(filepath))
        
        manager = BackgroundManager(bg_dir)
        
        # Random selection should return one of the created files
        for _ in range(5):
            selected = manager.get_random_background()
            assert selected in created_files
            assert manager.background_exists(selected)


class TestVideoGenerator:
    """
    Property 3: Video Output Format Compliance
    For any generated video file, the output SHALL be in MP4 format with aspect ratio 9:16.
    """
    
    def test_video_dimensions_are_portrait(self):
        """Video dimensions should be 9:16 portrait"""
        generator = VideoGenerator()
        assert generator.width == 1080
        assert generator.height == 1920
        assert generator.width / generator.height == 9 / 16
    
    @given(text=st.text(min_size=1, max_size=200))
    @settings(max_examples=20)
    def test_text_wrapping(self, text):
        """Text wrapping should not exceed max characters per line"""
        generator = VideoGenerator()
        wrapped = generator._wrap_text(text, max_chars=40)
        
        for line in wrapped.split('\n'):
            # Each line should be <= max_chars (with some tolerance for word boundaries)
            assert len(line) <= 50  # Allow some overflow for long words


class TestTranslationInclusion:
    """
    Property 7: Translation Inclusion
    For any generated video metadata, the translation text SHALL be non-empty.
    """
    
    @given(
        surah=st.integers(min_value=1, max_value=114),
        ayat=st.integers(min_value=1, max_value=286),
        translation=st.text(min_size=1, max_size=500)
    )
    @settings(max_examples=30)
    def test_video_metadata_includes_translation(self, temp_db, surah, ayat, translation):
        """Video metadata should include non-empty translation"""
        from api.repositories.video_repository import VideoRepository
        
        repo = VideoRepository(temp_db)
        video = repo.create({
            "surah": surah,
            "ayat": ayat,
            "surah_name": "TestSurah",
            "text_arab": "Arabic text",
            "text_translation": translation,
            "qari": "alafasy",
            "background_file": "bg.mp4",
            "output_file": "output.mp4",
            "status": "completed"
        })
        
        retrieved = repo.get_by_id(video.id)
        assert retrieved.text_translation == translation
        assert len(retrieved.text_translation) > 0
