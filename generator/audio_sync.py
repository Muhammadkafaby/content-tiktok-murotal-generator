"""
Audio-Text Synchronization Service for Quran Video Generator.

This module provides functionality to synchronize Arabic text and Indonesian
translation display with audio murotal timing.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import os


@dataclass
class TextTiming:
    """Timing data for text display synchronized with audio."""
    arab_start: float = 0.0          # When Arabic text starts appearing (seconds)
    arab_fade_in: float = 0.5        # Duration of Arabic text fade-in (seconds)
    translation_start: float = 0.0   # When translation starts appearing (seconds)
    translation_fade_in: float = 0.5 # Duration of translation fade-in (seconds)
    fade_out_start: float = 0.0      # When all text starts fading out (seconds)
    total_duration: float = 0.0      # Total video/audio duration (seconds)


@dataclass
class AudioSegment:
    """Represents a segment of audio with timing information."""
    start: float                     # Segment start time (seconds)
    end: float                       # Segment end time (seconds)
    text_arab: str = ""              # Arabic text for this segment
    text_translation: str = ""       # Translation text for this segment (optional)


@dataclass
class AudioTimingData:
    """Complete timing data for audio-text synchronization."""
    total_duration: float = 0.0
    segments: List[AudioSegment] = field(default_factory=list)
    silence_intervals: List[Tuple[float, float]] = field(default_factory=list)
    text_timing: TextTiming = field(default_factory=TextTiming)


class AudioSyncService:
    """Service for calculating text timing synchronized with audio."""
    
    # Animation duration constraints (seconds)
    MIN_FADE_DURATION = 0.3
    MAX_FADE_DURATION = 1.0
    DEFAULT_FADE_DURATION = 0.5
    
    # Translation timing (percentage of audio duration)
    TRANSLATION_START_RATIO = 0.7
    
    def __init__(self):
        self._librosa = None
        self._soundfile = None

    def _load_librosa(self):
        """Lazy load librosa to avoid import overhead."""
        if self._librosa is None:
            try:
                import librosa
                self._librosa = librosa
            except ImportError:
                raise ImportError("librosa is required for audio analysis. Install with: pip install librosa")
        return self._librosa
    
    def _load_soundfile(self):
        """Lazy load soundfile for audio reading."""
        if self._soundfile is None:
            try:
                import soundfile as sf
                self._soundfile = sf
            except ImportError:
                raise ImportError("soundfile is required for audio reading. Install with: pip install soundfile")
        return self._soundfile

    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get the duration of an audio file in seconds.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Duration in seconds
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            librosa = self._load_librosa()
            duration = librosa.get_duration(path=audio_path)
            return float(duration)
        except Exception as e:
            # Fallback: try using pydub
            try:
                from pydub import AudioSegment as PydubSegment
                audio = PydubSegment.from_file(audio_path)
                return len(audio) / 1000.0  # Convert ms to seconds
            except Exception:
                raise RuntimeError(f"Failed to get audio duration: {e}")

    def calculate_text_timing(
        self,
        audio_duration: float,
        text_arab: str = "",
        text_translation: str = ""
    ) -> TextTiming:
        """
        Calculate timing for text display synchronized with audio.
        
        Strategy:
        1. Arabic text appears at start, fades in over 0.5s
        2. Arabic text stays visible during audio playback
        3. Translation appears after ~70% of audio duration
        4. Both texts fade out together at end
        
        Args:
            audio_duration: Total audio duration in seconds
            text_arab: Arabic text (used for timing adjustments)
            text_translation: Translation text (used for timing adjustments)
            
        Returns:
            TextTiming object with calculated timings
        """
        if audio_duration <= 0:
            return TextTiming()
        
        # Calculate fade duration based on audio length
        # Shorter audio = shorter fades
        fade_duration = min(
            self.MAX_FADE_DURATION,
            max(self.MIN_FADE_DURATION, audio_duration * 0.1)
        )
        
        # Arabic text starts immediately
        arab_start = 0.0
        arab_fade_in = fade_duration
        
        # Translation appears after 70% of audio, but ensure enough time to read
        # Minimum 1 second before end for translation to appear
        translation_start = max(
            arab_fade_in + 0.5,  # At least 0.5s after Arabic appears
            min(
                audio_duration * self.TRANSLATION_START_RATIO,
                audio_duration - 2.0  # At least 2s before end
            )
        )
        translation_fade_in = fade_duration
        
        # Fade out starts near the end
        fade_out_start = max(0, audio_duration - fade_duration)
        
        return TextTiming(
            arab_start=arab_start,
            arab_fade_in=arab_fade_in,
            translation_start=translation_start,
            translation_fade_in=translation_fade_in,
            fade_out_start=fade_out_start,
            total_duration=audio_duration
        )


    def calculate_timing_from_file(
        self,
        audio_path: str,
        text_arab: str = "",
        text_translation: str = ""
    ) -> TextTiming:
        """
        Calculate text timing from an audio file.
        
        Args:
            audio_path: Path to the audio file
            text_arab: Arabic text
            text_translation: Translation text
            
        Returns:
            TextTiming object with calculated timings
        """
        duration = self.get_audio_duration(audio_path)
        return self.calculate_text_timing(duration, text_arab, text_translation)

    def analyze_audio(self, audio_path: str) -> AudioTimingData:
        """
        Analyze audio file and return complete timing data.
        
        This is the main entry point for audio analysis. It:
        1. Gets audio duration
        2. Calculates text timing
        3. Optionally detects segments (for longer audio)
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            AudioTimingData with complete timing information
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        duration = self.get_audio_duration(audio_path)
        text_timing = self.calculate_text_timing(duration)
        
        return AudioTimingData(
            total_duration=duration,
            segments=[],  # Will be populated by segment detection if needed
            silence_intervals=[],
            text_timing=text_timing
        )

    def validate_timing(self, timing: TextTiming) -> bool:
        """
        Validate that timing data is correct and consistent.
        
        Checks:
        - translation_start >= arab_start
        - fade durations are within bounds
        - fade_out_start is before total_duration
        
        Args:
            timing: TextTiming object to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Translation must appear after or at same time as Arabic
        if timing.translation_start < timing.arab_start:
            return False
        
        # Fade durations must be within bounds
        if not (self.MIN_FADE_DURATION <= timing.arab_fade_in <= self.MAX_FADE_DURATION):
            return False
        if not (self.MIN_FADE_DURATION <= timing.translation_fade_in <= self.MAX_FADE_DURATION):
            return False
        
        # Fade out must start before or at total duration
        if timing.fade_out_start > timing.total_duration:
            return False
        
        # Total duration must be positive
        if timing.total_duration <= 0:
            return False
        
        return True


# Singleton instance for convenience
_audio_sync_service: Optional[AudioSyncService] = None


def get_audio_sync_service() -> AudioSyncService:
    """Get or create the AudioSyncService singleton."""
    global _audio_sync_service
    if _audio_sync_service is None:
        _audio_sync_service = AudioSyncService()
    return _audio_sync_service



class AudioSegmentDetector:
    """
    Detects natural pauses/segments in audio for text synchronization.
    
    Uses librosa to analyze audio and find silence intervals that
    correspond to natural pauses in qari recitation.
    """
    
    # Default parameters for silence detection
    DEFAULT_TOP_DB = 30  # Threshold below reference to consider as silence
    DEFAULT_MIN_SILENCE_DURATION = 0.3  # Minimum silence duration in seconds
    
    def __init__(self, top_db: int = DEFAULT_TOP_DB, min_silence_duration: float = DEFAULT_MIN_SILENCE_DURATION):
        """
        Initialize the segment detector.
        
        Args:
            top_db: Threshold in dB below reference to consider as silence
            min_silence_duration: Minimum duration of silence to consider as segment boundary
        """
        self.top_db = top_db
        self.min_silence_duration = min_silence_duration
        self._librosa = None
    
    def _load_librosa(self):
        """Lazy load librosa."""
        if self._librosa is None:
            try:
                import librosa
                self._librosa = librosa
            except ImportError:
                raise ImportError("librosa is required for segment detection")
        return self._librosa

    def detect_segments(self, audio_path: str) -> List[AudioSegment]:
        """
        Detect natural segments in audio based on silence intervals.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            List of AudioSegment objects with timing information
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        librosa = self._load_librosa()
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        
        # Detect non-silent intervals
        intervals = librosa.effects.split(y, top_db=self.top_db)
        
        segments = []
        for start_sample, end_sample in intervals:
            start_time = float(start_sample) / sr
            end_time = float(end_sample) / sr
            
            # Only include segments longer than minimum duration
            if (end_time - start_time) >= self.min_silence_duration:
                segments.append(AudioSegment(
                    start=start_time,
                    end=end_time,
                    text_arab="",
                    text_translation=""
                ))
        
        return segments

    def detect_silence_intervals(self, audio_path: str) -> List[Tuple[float, float]]:
        """
        Detect silence intervals in audio.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            List of (start, end) tuples for silence intervals
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        librosa = self._load_librosa()
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        total_duration = len(y) / sr
        
        # Detect non-silent intervals
        non_silent = librosa.effects.split(y, top_db=self.top_db)
        
        # Convert to silence intervals
        silence_intervals = []
        prev_end = 0.0
        
        for start_sample, end_sample in non_silent:
            start_time = float(start_sample) / sr
            
            # If there's a gap between previous end and current start, it's silence
            if start_time > prev_end + 0.01:  # Small tolerance
                silence_intervals.append((prev_end, start_time))
            
            prev_end = float(end_sample) / sr
        
        # Check for silence at the end
        if prev_end < total_duration - 0.01:
            silence_intervals.append((prev_end, total_duration))
        
        return silence_intervals

    def validate_segments(self, segments: List[AudioSegment]) -> bool:
        """
        Validate that segments are properly ordered and don't overlap.
        
        Args:
            segments: List of AudioSegment objects
            
        Returns:
            True if valid, False otherwise
        """
        if not segments:
            return True
        
        for i, segment in enumerate(segments):
            # Each segment must have end > start
            if segment.end <= segment.start:
                return False
            
            # Segments must not overlap
            if i > 0:
                prev_segment = segments[i - 1]
                if segment.start < prev_segment.end:
                    return False
        
        return True


    def split_text_by_segments(
        self,
        text: str,
        segments: List[AudioSegment],
        is_arabic: bool = True
    ) -> List[AudioSegment]:
        """
        Split text into segments based on detected audio segments.
        
        For Arabic text, splits by words proportionally.
        For translation, can split by sentences or proportionally.
        
        Args:
            text: Text to split
            segments: Audio segments with timing
            is_arabic: Whether the text is Arabic (affects splitting logic)
            
        Returns:
            List of AudioSegment with text assigned
        """
        if not segments or not text:
            return segments
        
        # Split text into words
        words = text.split()
        if not words:
            return segments
        
        # Calculate total audio duration from segments
        total_segment_duration = sum(s.end - s.start for s in segments)
        
        # Distribute words proportionally across segments
        result_segments = []
        word_index = 0
        
        for segment in segments:
            segment_duration = segment.end - segment.start
            segment_ratio = segment_duration / total_segment_duration if total_segment_duration > 0 else 0
            
            # Calculate how many words for this segment
            words_for_segment = max(1, int(len(words) * segment_ratio))
            
            # Get words for this segment
            segment_words = words[word_index:word_index + words_for_segment]
            word_index += words_for_segment
            
            # Create new segment with text
            new_segment = AudioSegment(
                start=segment.start,
                end=segment.end,
                text_arab=(" ".join(segment_words) if is_arabic else ""),
                text_translation=("" if is_arabic else " ".join(segment_words))
            )
            result_segments.append(new_segment)
        
        # Assign remaining words to last segment
        if word_index < len(words) and result_segments:
            remaining = " ".join(words[word_index:])
            last = result_segments[-1]
            if is_arabic:
                last.text_arab = f"{last.text_arab} {remaining}".strip()
            else:
                last.text_translation = f"{last.text_translation} {remaining}".strip()
        
        return result_segments


def analyze_audio_with_segments(
    audio_path: str,
    text_arab: str = "",
    text_translation: str = ""
) -> AudioTimingData:
    """
    Convenience function to analyze audio and detect segments.
    
    Args:
        audio_path: Path to audio file
        text_arab: Arabic text to split across segments
        text_translation: Translation text
        
    Returns:
        AudioTimingData with segments and timing
    """
    sync_service = get_audio_sync_service()
    detector = AudioSegmentDetector()
    
    # Get basic timing
    timing_data = sync_service.analyze_audio(audio_path)
    
    # Detect segments
    segments = detector.detect_segments(audio_path)
    
    # Split text across segments if provided
    if text_arab and segments:
        segments = detector.split_text_by_segments(text_arab, segments, is_arabic=True)
    
    # Detect silence intervals
    silence_intervals = detector.detect_silence_intervals(audio_path)
    
    timing_data.segments = segments
    timing_data.silence_intervals = silence_intervals
    
    return timing_data
