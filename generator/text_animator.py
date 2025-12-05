"""
Text Animation Module for Quran Video Generator.

Provides fade-in/fade-out animations for text overlays synchronized with audio.
"""

from dataclasses import dataclass
from typing import Callable, Optional
from enum import Enum


class AnimationType(Enum):
    """Types of text animations."""
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SLIDE_UP = "slide_up"
    NONE = "none"


@dataclass
class AnimationConfig:
    """Configuration for a text animation."""
    animation_type: AnimationType
    start_time: float      # When animation starts (seconds)
    duration: float        # Animation duration (seconds)
    
    # For slide animations
    start_y_offset: float = 0.0  # Starting Y offset (pixels or percentage)
    end_y_offset: float = 0.0    # Ending Y offset


@dataclass
class TextClipConfig:
    """Configuration for an animated text clip."""
    text: str
    start_time: float           # When text appears (seconds)
    end_time: float             # When text disappears (seconds)
    fade_in_duration: float     # Fade-in duration (seconds)
    fade_out_duration: float    # Fade-out duration (seconds)
    position: tuple = ("center", "center")  # Position on screen
    font_size: int = 50
    font_color: str = "white"
    font: str = "Arial"
    stroke_color: str = "black"
    stroke_width: int = 2


class TextAnimator:
    """
    Creates animated text clips with fade effects for video composition.
    
    Supports:
    - Fade-in animation (opacity 0 -> 1)
    - Fade-out animation (opacity 1 -> 0)
    - Slide-up animation (for translation text)
    """
    
    # Animation constraints
    MIN_FADE_DURATION = 0.3
    MAX_FADE_DURATION = 1.0

    def __init__(self):
        self._moviepy = None
    
    def _load_moviepy(self):
        """Lazy load moviepy."""
        if self._moviepy is None:
            try:
                import moviepy.editor as mpy
                self._moviepy = mpy
            except ImportError:
                raise ImportError("moviepy is required for text animation")
        return self._moviepy

    def validate_fade_duration(self, duration: float) -> float:
        """
        Validate and clamp fade duration to acceptable range.
        
        Args:
            duration: Requested fade duration
            
        Returns:
            Clamped duration within MIN_FADE_DURATION and MAX_FADE_DURATION
        """
        return max(self.MIN_FADE_DURATION, min(self.MAX_FADE_DURATION, duration))

    def calculate_opacity(
        self,
        current_time: float,
        start_time: float,
        end_time: float,
        fade_in_duration: float,
        fade_out_duration: float
    ) -> float:
        """
        Calculate opacity at a given time for fade animations.
        
        Args:
            current_time: Current time in video (seconds)
            start_time: When text starts appearing
            end_time: When text finishes disappearing
            fade_in_duration: Duration of fade-in
            fade_out_duration: Duration of fade-out
            
        Returns:
            Opacity value between 0.0 and 1.0
        """
        # Before start - invisible
        if current_time < start_time:
            return 0.0
        
        # After end - invisible
        if current_time > end_time:
            return 0.0
        
        # During fade-in
        fade_in_end = start_time + fade_in_duration
        if current_time < fade_in_end:
            progress = (current_time - start_time) / fade_in_duration
            return min(1.0, max(0.0, progress))
        
        # During fade-out
        fade_out_start = end_time - fade_out_duration
        if current_time > fade_out_start:
            progress = (end_time - current_time) / fade_out_duration
            return min(1.0, max(0.0, progress))
        
        # Fully visible
        return 1.0

    def create_fade_function(
        self,
        start_time: float,
        end_time: float,
        fade_in_duration: float,
        fade_out_duration: float
    ) -> Callable[[float], float]:
        """
        Create a function that returns opacity at any given time.
        
        This is used with moviepy's fl method for applying animations.
        
        Args:
            start_time: When text starts appearing
            end_time: When text finishes disappearing
            fade_in_duration: Duration of fade-in
            fade_out_duration: Duration of fade-out
            
        Returns:
            Function that takes time and returns opacity
        """
        def opacity_func(t: float) -> float:
            return self.calculate_opacity(
                t, start_time, end_time, fade_in_duration, fade_out_duration
            )
        return opacity_func


    def create_animated_text_clip(
        self,
        config: TextClipConfig,
        video_duration: float
    ):
        """
        Create a text clip with fade-in and fade-out animations.
        
        Args:
            config: TextClipConfig with text and timing settings
            video_duration: Total video duration for clip timing
            
        Returns:
            MoviePy TextClip with fade animations applied
        """
        mpy = self._load_moviepy()
        
        # Validate fade durations
        fade_in = self.validate_fade_duration(config.fade_in_duration)
        fade_out = self.validate_fade_duration(config.fade_out_duration)
        
        # Calculate clip duration
        clip_duration = config.end_time - config.start_time
        if clip_duration <= 0:
            raise ValueError("end_time must be greater than start_time")
        
        # Create base text clip
        txt_clip = mpy.TextClip(
            config.text,
            fontsize=config.font_size,
            color=config.font_color,
            font=config.font,
            stroke_color=config.stroke_color,
            stroke_width=config.stroke_width,
            method='caption',
            size=(1000, None)  # Width constraint for wrapping
        )
        
        # Set duration and start time
        txt_clip = txt_clip.set_duration(clip_duration)
        txt_clip = txt_clip.set_start(config.start_time)
        txt_clip = txt_clip.set_position(config.position)
        
        # Apply fade-in effect
        if fade_in > 0:
            txt_clip = txt_clip.crossfadein(fade_in)
        
        # Apply fade-out effect
        if fade_out > 0:
            txt_clip = txt_clip.crossfadeout(fade_out)
        
        return txt_clip

    def create_arabic_text_clip(
        self,
        text: str,
        start_time: float,
        end_time: float,
        fade_in: float = 0.5,
        fade_out: float = 0.5,
        font_size: int = 60,
        position: tuple = ("center", 0.3)
    ):
        """
        Create an animated Arabic text clip.
        
        Args:
            text: Arabic text to display
            start_time: When text appears
            end_time: When text disappears
            fade_in: Fade-in duration
            fade_out: Fade-out duration
            font_size: Font size
            position: Position on screen (x, y) or named positions
            
        Returns:
            Animated TextClip
        """
        config = TextClipConfig(
            text=text,
            start_time=start_time,
            end_time=end_time,
            fade_in_duration=fade_in,
            fade_out_duration=fade_out,
            position=position,
            font_size=font_size,
            font_color="white",
            font="Arial",  # Will be replaced with Arabic font
            stroke_color="black",
            stroke_width=2
        )
        return self.create_animated_text_clip(config, end_time)

    def create_translation_text_clip(
        self,
        text: str,
        start_time: float,
        end_time: float,
        fade_in: float = 0.5,
        fade_out: float = 0.5,
        font_size: int = 40,
        position: tuple = ("center", 0.7)
    ):
        """
        Create an animated translation text clip.
        
        Args:
            text: Translation text to display
            start_time: When text appears
            end_time: When text disappears
            fade_in: Fade-in duration
            fade_out: Fade-out duration
            font_size: Font size
            position: Position on screen
            
        Returns:
            Animated TextClip
        """
        config = TextClipConfig(
            text=text,
            start_time=start_time,
            end_time=end_time,
            fade_in_duration=fade_in,
            fade_out_duration=fade_out,
            position=position,
            font_size=font_size,
            font_color="white",
            font="Arial",
            stroke_color="black",
            stroke_width=1
        )
        return self.create_animated_text_clip(config, end_time)



def create_synced_text_clips(
    text_arab: str,
    text_translation: str,
    audio_duration: float,
    arab_start: float = 0.0,
    translation_start: float = None,
    fade_in: float = 0.5,
    fade_out: float = 0.5
) -> tuple:
    """
    Create synchronized Arabic and translation text clips.
    
    Convenience function that creates both text clips with proper timing.
    
    Args:
        text_arab: Arabic text
        text_translation: Translation text
        audio_duration: Total audio/video duration
        arab_start: When Arabic text appears (default: 0)
        translation_start: When translation appears (default: 70% of duration)
        fade_in: Fade-in duration
        fade_out: Fade-out duration
        
    Returns:
        Tuple of (arabic_clip, translation_clip)
    """
    animator = TextAnimator()
    
    # Default translation start to 70% of duration
    if translation_start is None:
        translation_start = audio_duration * 0.7
    
    # Ensure translation appears after Arabic
    translation_start = max(translation_start, arab_start + fade_in)
    
    # Create Arabic text clip
    arabic_clip = animator.create_arabic_text_clip(
        text=text_arab,
        start_time=arab_start,
        end_time=audio_duration,
        fade_in=fade_in,
        fade_out=fade_out
    )
    
    # Create translation text clip
    translation_clip = animator.create_translation_text_clip(
        text=text_translation,
        start_time=translation_start,
        end_time=audio_duration,
        fade_in=fade_in,
        fade_out=fade_out
    )
    
    return arabic_clip, translation_clip


def validate_animation_timing(
    fade_in: float,
    fade_out: float,
    min_duration: float = 0.3,
    max_duration: float = 1.0
) -> tuple:
    """
    Validate and clamp animation timing values.
    
    Args:
        fade_in: Requested fade-in duration
        fade_out: Requested fade-out duration
        min_duration: Minimum allowed duration
        max_duration: Maximum allowed duration
        
    Returns:
        Tuple of (validated_fade_in, validated_fade_out)
    """
    valid_fade_in = max(min_duration, min(max_duration, fade_in))
    valid_fade_out = max(min_duration, min(max_duration, fade_out))
    return valid_fade_in, valid_fade_out
