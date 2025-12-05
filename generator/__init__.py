# Video Generator Module
from generator.quran_service import QuranService
from generator.video_generator import VideoGenerator
from generator.background_manager import BackgroundManager
from generator.audio_sync import (
    AudioSyncService,
    AudioSegmentDetector,
    TextTiming,
    AudioSegment,
    AudioTimingData,
    get_audio_sync_service,
    analyze_audio_with_segments
)
from generator.text_animator import (
    TextAnimator,
    TextClipConfig,
    AnimationType,
    AnimationConfig,
    create_synced_text_clips,
    validate_animation_timing
)

__all__ = [
    "QuranService",
    "VideoGenerator", 
    "BackgroundManager",
    "AudioSyncService",
    "AudioSegmentDetector",
    "TextTiming",
    "AudioSegment",
    "AudioTimingData",
    "get_audio_sync_service",
    "analyze_audio_with_segments",
    "TextAnimator",
    "TextClipConfig",
    "AnimationType",
    "AnimationConfig",
    "create_synced_text_clips",
    "validate_animation_timing"
]
