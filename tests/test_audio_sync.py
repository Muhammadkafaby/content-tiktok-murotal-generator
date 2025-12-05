"""
Property-based tests for Audio-Text Synchronization Service.

Tests the correctness properties defined in the design document:
- Property 19: Audio-Text Synchronization
- Property 20: Translation Timing Sequence
- Property 21: Text Duration Alignment
- Property 22: Smooth Text Animation
- Property 23: Segment Timing Validity

**Feature: quran-video-generator**
**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**
"""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from hypothesis import given, strategies as st, settings, assume

# Import directly from audio_sync module to avoid video_generator dependencies
from generator.audio_sync import (
    AudioSyncService,
    AudioSegmentDetector,
    TextTiming,
    AudioSegment,
    AudioTimingData,
    get_audio_sync_service
)
from generator.text_animator import (
    TextAnimator,
    validate_animation_timing
)


# Strategy for generating realistic audio durations (1 second to 5 minutes)
audio_duration_strategy = st.floats(min_value=1.0, max_value=300.0, allow_nan=False, allow_infinity=False)

# Strategy for generating Arabic text (non-empty strings)
arabic_text_strategy = st.text(min_size=1, max_size=500).filter(lambda x: x.strip())

# Strategy for generating translation text
translation_text_strategy = st.text(min_size=1, max_size=1000).filter(lambda x: x.strip())

# Strategy for fade durations
fade_duration_strategy = st.floats(min_value=0.1, max_value=2.0, allow_nan=False, allow_infinity=False)


class TestAudioTextSynchronization:
    """
    **Feature: quran-video-generator, Property 19: Audio-Text Synchronization**
    **Validates: Requirements 8.1**
    
    *For any* generated video, the Arabic text SHALL appear synchronized 
    with the start of audio playback (within 0.5 second tolerance).
    """
    
    @given(audio_duration=audio_duration_strategy)
    @settings(max_examples=100)
    def test_arabic_text_starts_at_audio_start(self, audio_duration: float):
        """Arabic text should start at or very close to audio start (within 0.5s)."""
        service = AudioSyncService()
        timing = service.calculate_text_timing(audio_duration)
        
        # Property: arab_start should be within 0.5 seconds of audio start (0.0)
        assert timing.arab_start >= 0.0, "Arabic text cannot start before audio"
        assert timing.arab_start <= 0.5, f"Arabic text should start within 0.5s of audio start, got {timing.arab_start}"
    
    @given(audio_duration=audio_duration_strategy)
    @settings(max_examples=100)
    def test_timing_total_duration_matches_audio(self, audio_duration: float):
        """Total timing duration should match audio duration."""
        service = AudioSyncService()
        timing = service.calculate_text_timing(audio_duration)
        
        # Property: total_duration should equal audio_duration
        assert timing.total_duration == audio_duration, \
            f"Total duration {timing.total_duration} should match audio {audio_duration}"



class TestTranslationTimingSequence:
    """
    **Feature: quran-video-generator, Property 20: Translation Timing Sequence**
    **Validates: Requirements 8.2**
    
    *For any* generated video, the Indonesian translation SHALL appear 
    after the Arabic text has been displayed (translation_start >= arab_start).
    """
    
    @given(audio_duration=audio_duration_strategy)
    @settings(max_examples=100)
    def test_translation_appears_after_arabic(self, audio_duration: float):
        """Translation should always appear after or at same time as Arabic text."""
        service = AudioSyncService()
        timing = service.calculate_text_timing(audio_duration)
        
        # Property: translation_start >= arab_start
        assert timing.translation_start >= timing.arab_start, \
            f"Translation start ({timing.translation_start}) must be >= Arabic start ({timing.arab_start})"
    
    @given(audio_duration=audio_duration_strategy)
    @settings(max_examples=100)
    def test_translation_appears_after_arabic_fade_in(self, audio_duration: float):
        """Translation should appear after Arabic text has faded in."""
        service = AudioSyncService()
        timing = service.calculate_text_timing(audio_duration)
        
        # Property: translation_start >= arab_start + arab_fade_in (with small tolerance)
        arab_visible_time = timing.arab_start + timing.arab_fade_in
        # Allow small tolerance for very short audio
        tolerance = 0.1 if audio_duration < 3.0 else 0.0
        
        assert timing.translation_start >= arab_visible_time - tolerance, \
            f"Translation ({timing.translation_start}) should appear after Arabic is visible ({arab_visible_time})"


class TestTextDurationAlignment:
    """
    **Feature: quran-video-generator, Property 21: Text Duration Alignment**
    **Validates: Requirements 8.5**
    
    *For any* generated video, the total text display duration SHALL match 
    the audio duration (text ends when audio ends, within 1 second tolerance).
    """
    
    @given(audio_duration=audio_duration_strategy)
    @settings(max_examples=100)
    def test_text_ends_with_audio(self, audio_duration: float):
        """Text should end when audio ends (within 1 second tolerance)."""
        service = AudioSyncService()
        timing = service.calculate_text_timing(audio_duration)
        
        # Property: fade_out_start + fade_duration should be close to total_duration
        # The text should be fully faded out by the end of audio
        text_end_time = timing.fade_out_start + timing.arab_fade_in  # Using fade_in as proxy for fade_out duration
        
        # Within 1 second tolerance
        assert abs(text_end_time - timing.total_duration) <= 1.0, \
            f"Text end ({text_end_time}) should be within 1s of audio end ({timing.total_duration})"
    
    @given(audio_duration=audio_duration_strategy)
    @settings(max_examples=100)
    def test_fade_out_starts_before_end(self, audio_duration: float):
        """Fade out should start before the total duration ends."""
        service = AudioSyncService()
        timing = service.calculate_text_timing(audio_duration)
        
        # Property: fade_out_start <= total_duration
        assert timing.fade_out_start <= timing.total_duration, \
            f"Fade out start ({timing.fade_out_start}) must be <= total duration ({timing.total_duration})"



class TestSmoothTextAnimation:
    """
    **Feature: quran-video-generator, Property 22: Smooth Text Animation**
    **Validates: Requirements 8.4**
    
    *For any* text transition in the video, the fade animation duration 
    SHALL be between 0.3 and 1.0 seconds for smooth visual experience.
    """
    
    @given(audio_duration=audio_duration_strategy)
    @settings(max_examples=100)
    def test_arabic_fade_in_within_bounds(self, audio_duration: float):
        """Arabic fade-in duration should be between 0.3 and 1.0 seconds."""
        service = AudioSyncService()
        timing = service.calculate_text_timing(audio_duration)
        
        # Property: 0.3 <= arab_fade_in <= 1.0
        assert service.MIN_FADE_DURATION <= timing.arab_fade_in <= service.MAX_FADE_DURATION, \
            f"Arabic fade-in ({timing.arab_fade_in}) must be between {service.MIN_FADE_DURATION} and {service.MAX_FADE_DURATION}"
    
    @given(audio_duration=audio_duration_strategy)
    @settings(max_examples=100)
    def test_translation_fade_in_within_bounds(self, audio_duration: float):
        """Translation fade-in duration should be between 0.3 and 1.0 seconds."""
        service = AudioSyncService()
        timing = service.calculate_text_timing(audio_duration)
        
        # Property: 0.3 <= translation_fade_in <= 1.0
        assert service.MIN_FADE_DURATION <= timing.translation_fade_in <= service.MAX_FADE_DURATION, \
            f"Translation fade-in ({timing.translation_fade_in}) must be between {service.MIN_FADE_DURATION} and {service.MAX_FADE_DURATION}"
    
    @given(
        fade_in=fade_duration_strategy,
        fade_out=fade_duration_strategy
    )
    @settings(max_examples=100)
    def test_validate_animation_timing_clamps_values(self, fade_in: float, fade_out: float):
        """validate_animation_timing should clamp values to valid range."""
        valid_in, valid_out = validate_animation_timing(fade_in, fade_out)
        
        # Property: output should always be within bounds
        assert 0.3 <= valid_in <= 1.0, f"Validated fade_in ({valid_in}) out of bounds"
        assert 0.3 <= valid_out <= 1.0, f"Validated fade_out ({valid_out}) out of bounds"


class TestSegmentTimingValidity:
    """
    **Feature: quran-video-generator, Property 23: Segment Timing Validity**
    **Validates: Requirements 8.3**
    
    *For any* audio segment detected, the segment end time SHALL be greater 
    than segment start time, and segments SHALL not overlap.
    """
    
    @given(
        start=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        duration=st.floats(min_value=0.1, max_value=50.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_segment_end_greater_than_start(self, start: float, duration: float):
        """Each segment's end time should be greater than its start time."""
        end = start + duration
        segment = AudioSegment(start=start, end=end)
        
        # Property: end > start
        assert segment.end > segment.start, \
            f"Segment end ({segment.end}) must be > start ({segment.start})"
    
    @given(
        segments_data=st.lists(
            st.tuples(
                st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
                st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False)
            ),
            min_size=2,
            max_size=10
        )
    )
    @settings(max_examples=50)
    def test_segments_do_not_overlap_when_sorted(self, segments_data):
        """Properly ordered segments should not overlap."""
        # Create segments from data
        segments = []
        current_start = 0.0
        for _, duration in segments_data:
            segment = AudioSegment(start=current_start, end=current_start + duration)
            segments.append(segment)
            current_start = segment.end + 0.1  # Small gap between segments
        
        # Validate using detector
        detector = AudioSegmentDetector()
        is_valid = detector.validate_segments(segments)
        
        # Property: properly constructed segments should be valid
        assert is_valid, "Properly ordered non-overlapping segments should be valid"
    
    def test_overlapping_segments_are_invalid(self):
        """Overlapping segments should be detected as invalid."""
        # Create overlapping segments
        segments = [
            AudioSegment(start=0.0, end=2.0),
            AudioSegment(start=1.5, end=3.0),  # Overlaps with first
        ]
        
        detector = AudioSegmentDetector()
        is_valid = detector.validate_segments(segments)
        
        # Property: overlapping segments should be invalid
        assert not is_valid, "Overlapping segments should be invalid"
    
    def test_invalid_segment_end_before_start(self):
        """Segment with end <= start should be invalid."""
        segments = [
            AudioSegment(start=2.0, end=1.0),  # Invalid: end < start
        ]
        
        detector = AudioSegmentDetector()
        is_valid = detector.validate_segments(segments)
        
        # Property: segment with end <= start should be invalid
        assert not is_valid, "Segment with end <= start should be invalid"



class TestTimingValidation:
    """Additional tests for timing validation."""
    
    @given(audio_duration=audio_duration_strategy)
    @settings(max_examples=100)
    def test_timing_validation_passes_for_valid_timing(self, audio_duration: float):
        """Valid timing from calculate_text_timing should pass validation."""
        service = AudioSyncService()
        timing = service.calculate_text_timing(audio_duration)
        
        # Property: timing from service should always be valid
        assert service.validate_timing(timing), \
            f"Timing from calculate_text_timing should be valid: {timing}"
    
    def test_invalid_timing_negative_duration(self):
        """Timing with negative duration should be invalid."""
        service = AudioSyncService()
        timing = TextTiming(
            arab_start=0.0,
            arab_fade_in=0.5,
            translation_start=0.5,
            translation_fade_in=0.5,
            fade_out_start=0.0,
            total_duration=-1.0  # Invalid
        )
        
        assert not service.validate_timing(timing), \
            "Timing with negative duration should be invalid"
    
    def test_invalid_timing_translation_before_arabic(self):
        """Timing where translation starts before Arabic should be invalid."""
        service = AudioSyncService()
        timing = TextTiming(
            arab_start=1.0,
            arab_fade_in=0.5,
            translation_start=0.5,  # Before Arabic
            translation_fade_in=0.5,
            fade_out_start=4.0,
            total_duration=5.0
        )
        
        assert not service.validate_timing(timing), \
            "Timing where translation starts before Arabic should be invalid"


class TestTextAnimator:
    """Tests for TextAnimator opacity calculations."""
    
    @given(
        current_time=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        start_time=st.floats(min_value=0.0, max_value=5.0, allow_nan=False, allow_infinity=False),
        duration=st.floats(min_value=1.0, max_value=5.0, allow_nan=False, allow_infinity=False),
        fade_in=st.floats(min_value=0.3, max_value=1.0, allow_nan=False, allow_infinity=False),
        fade_out=st.floats(min_value=0.3, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_opacity_always_between_0_and_1(
        self, current_time: float, start_time: float, duration: float, 
        fade_in: float, fade_out: float
    ):
        """Opacity should always be between 0.0 and 1.0."""
        animator = TextAnimator()
        end_time = start_time + duration
        
        opacity = animator.calculate_opacity(
            current_time, start_time, end_time, fade_in, fade_out
        )
        
        # Property: opacity is always in [0.0, 1.0]
        assert 0.0 <= opacity <= 1.0, f"Opacity ({opacity}) must be between 0 and 1"
    
    def test_opacity_zero_before_start(self):
        """Opacity should be 0 before text starts appearing."""
        animator = TextAnimator()
        
        opacity = animator.calculate_opacity(
            current_time=0.5,
            start_time=1.0,
            end_time=5.0,
            fade_in_duration=0.5,
            fade_out_duration=0.5
        )
        
        assert opacity == 0.0, "Opacity should be 0 before start time"
    
    def test_opacity_zero_after_end(self):
        """Opacity should be 0 after text has disappeared."""
        animator = TextAnimator()
        
        opacity = animator.calculate_opacity(
            current_time=6.0,
            start_time=1.0,
            end_time=5.0,
            fade_in_duration=0.5,
            fade_out_duration=0.5
        )
        
        assert opacity == 0.0, "Opacity should be 0 after end time"
    
    def test_opacity_one_during_visible_period(self):
        """Opacity should be 1.0 during fully visible period."""
        animator = TextAnimator()
        
        opacity = animator.calculate_opacity(
            current_time=3.0,  # Middle of visible period
            start_time=1.0,
            end_time=5.0,
            fade_in_duration=0.5,
            fade_out_duration=0.5
        )
        
        assert opacity == 1.0, "Opacity should be 1.0 during fully visible period"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
