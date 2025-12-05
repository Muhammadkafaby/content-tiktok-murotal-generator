import os
import uuid
import tempfile
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from hijri_converter import Hijri, Gregorian

# Fix for Pillow 10+ compatibility with moviepy
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, vfx
from api.config import VIDEOS_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, DATA_DIR

# Import audio sync service for text-audio synchronization
from generator.audio_sync import get_audio_sync_service, TextTiming


class VideoGenerator:
    def __init__(self):
        self.output_dir = VIDEOS_DIR
        self.width = VIDEO_WIDTH
        self.height = VIDEO_HEIGHT
        self.fps = VIDEO_FPS
        self.logo_path = DATA_DIR / "assets" / "logo.png"
        self.min_video_duration = 10.0  # Minimum total video duration in seconds
        self.watermark_text = "@ruang.ayat"
        self.watermark_opacity = 0.4  # 40% opacity for better visibility
        self.fade_duration = 0.8  # Fade in/out duration in seconds
        self.bg_darken = 0.55  # Background darken level (55% brightness)
        
        # Audio sync service for text-audio synchronization
        self.audio_sync = get_audio_sync_service()
        # Indonesian day names
        self.day_names_id = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Ahad']
        self.day_names_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        # Indonesian month names
        self.month_names_id = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                               'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        # Hijri month names
        self.hijri_months = ['Muharram', 'Safar', 'Rabiul Awal', 'Rabiul Akhir', 
                            'Jumadil Awal', 'Jumadil Akhir', 'Rajab', 'Syaban',
                            'Ramadhan', 'Syawal', 'Dzulqaidah', 'Dzulhijjah']
        # Font paths for regular text
        self.font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        ]
        # Font paths for Arabic text (Amiri Quran - proper Hafs style)
        self.arabic_font_paths = [
            "/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf",
            "/usr/share/fonts/truetype/amiri/AmiriQuran-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
            "/usr/share/fonts/truetype/fonts-arabeyes/ae_AlArabiya.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    
    def _get_font(self, size: int, arabic: bool = False) -> ImageFont.FreeTypeFont:
        """Get available font"""
        font_list = self.arabic_font_paths if arabic else self.font_paths
        for font_path in font_list:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        # Fallback to default
        return ImageFont.load_default()
    
    def _create_text_image(
        self,
        text: str,
        fontsize: int,
        color: str = 'white',
        max_width: int = None,
        arabic: bool = False
    ) -> np.ndarray:
        """Create text image using PIL (no ImageMagick needed)"""
        if max_width is None:
            max_width = self.width - 100
        
        font = self._get_font(fontsize, arabic=arabic)
        
        # Wrap text
        wrapped_text = self._wrap_text_pil(text, font, max_width)
        
        # Calculate image size
        dummy_img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0] + 40
        text_height = bbox[3] - bbox[1] + 40
        
        # Create image with transparent background
        img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw text with shadow for better visibility
        shadow_offset = 2
        draw.multiline_text((20 + shadow_offset, 20 + shadow_offset), wrapped_text, 
                           font=font, fill=(0, 0, 0, 180), align='center')
        draw.multiline_text((20, 20), wrapped_text, font=font, fill=color, align='center')
        
        return np.array(img)
    
    def _create_aesthetic_text(
        self,
        text: str,
        fontsize: int,
        color: str = 'white',
        max_width: int = None,
        arabic: bool = False,
        italic_style: bool = False
    ) -> np.ndarray:
        """Create aesthetic text with soft shadow for wallpaper-style look"""
        if max_width is None:
            max_width = self.width - 80  # More padding for aesthetic
        
        font = self._get_font(fontsize, arabic=arabic)
        
        # Wrap text
        wrapped_text = self._wrap_text_pil(text, font, max_width)
        
        # Calculate image size
        dummy_img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0] + 60
        text_height = bbox[3] - bbox[1] + 50
        
        # Create image with transparent background
        img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw soft shadow (multiple layers for blur effect)
        shadow_color = (0, 0, 0, 60)
        for offset in [(3, 3), (2, 2), (4, 4)]:
            draw.multiline_text((30 + offset[0], 25 + offset[1]), wrapped_text, 
                               font=font, fill=shadow_color, align='center')
        
        # Draw main text
        draw.multiline_text((30, 25), wrapped_text, font=font, fill=color, align='center')
        
        return np.array(img)
    
    def _get_calendar_info(self) -> Dict[str, str]:
        """Get current date info in Masehi and Hijriah"""
        now = datetime.now()
        
        # Day name
        day_idx = now.weekday()
        day_id = self.day_names_id[day_idx]
        day_en = self.day_names_en[day_idx]
        
        # Masehi date
        masehi_day = now.day
        masehi_month = self.month_names_id[now.month - 1]
        masehi_year = now.year
        
        # Hijriah date
        hijri = Gregorian(now.year, now.month, now.day).to_hijri()
        hijri_day = hijri.day
        hijri_month = self.hijri_months[hijri.month - 1]
        hijri_year = hijri.year
        
        return {
            'day_id': day_id,
            'day_en': day_en,
            'masehi_day': masehi_day,
            'masehi_month': masehi_month,
            'masehi_year': masehi_year,
            'hijri_day': hijri_day,
            'hijri_month': hijri_month,
            'hijri_year': hijri_year
        }
    
    def _create_status_bar(self) -> np.ndarray:
        """Create iPhone-style status bar with signal, 5G, battery (right side only)"""
        bar_width = self.width
        bar_height = 44
        img = Image.new('RGBA', (bar_width, bar_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        font_5g = self._get_font(14)
        
        # Right side only - Signal bars, 5G, Battery
        right_x = bar_width - 30
        y_center = 18
        
        # Battery icon (outline rectangle with fill)
        bat_width, bat_height = 24, 12
        bat_x = right_x - bat_width
        draw.rounded_rectangle(
            [(bat_x, y_center), (bat_x + bat_width, y_center + bat_height)],
            radius=2, outline=(255, 255, 255, 255), width=1
        )
        # Battery cap
        draw.rectangle([(bat_x + bat_width, y_center + 3), (bat_x + bat_width + 2, y_center + 9)], 
                      fill=(255, 255, 255, 255))
        # Battery fill (full)
        draw.rectangle([(bat_x + 2, y_center + 2), (bat_x + bat_width - 2, y_center + bat_height - 2)], 
                      fill=(255, 255, 255, 255))
        
        # 5G text
        draw.text((bat_x - 30, y_center - 2), "5G", font=font_5g, fill=(255, 255, 255, 255))
        
        # Signal bars (4 bars increasing height)
        signal_x = bat_x - 70
        bar_gap = 3
        for i, h in enumerate([5, 8, 11, 14]):
            bx = signal_x + i * (3 + bar_gap)
            by = y_center + 14 - h
            draw.rounded_rectangle([(bx, by), (bx + 3, y_center + 14)], radius=1, fill=(255, 255, 255, 255))
        
        return np.array(img)
    
    def _create_lock_icon(self) -> np.ndarray:
        """Create lock icon for lock screen"""
        icon_size = 50
        img = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw lock icon using shapes
        # Lock body (rounded rectangle)
        draw.rounded_rectangle([(10, 22), (40, 45)], radius=5, fill=(255, 255, 255, 200))
        # Lock shackle (arc)
        draw.arc([(15, 8), (35, 28)], start=180, end=0, fill=(255, 255, 255, 200), width=4)
        # Keyhole
        draw.ellipse([(22, 28), (28, 34)], fill=(0, 0, 0, 150))
        draw.rectangle([(24, 32), (26, 40)], fill=(0, 0, 0, 150))
        
        return np.array(img)
    
    def _create_bottom_bar(self) -> np.ndarray:
        """Create iPhone-style bottom bar with flashlight and camera icons"""
        bar_width = self.width
        bar_height = 120
        img = Image.new('RGBA', (bar_width, bar_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        font_hint = self._get_font(16)
        
        # Button settings
        button_size = 50
        button_y = 10
        
        # Left button (flashlight) - dark rounded square
        left_x = 35
        draw.rounded_rectangle(
            [(left_x, button_y), (left_x + button_size, button_y + button_size)],
            radius=14,
            fill=(50, 50, 50, 200)
        )
        # Flashlight icon - simple torch shape
        cx, cy = left_x + button_size // 2, button_y + button_size // 2
        # Torch head (trapezoid-ish)
        draw.polygon([(cx - 6, cy - 12), (cx + 6, cy - 12), (cx + 4, cy + 2), (cx - 4, cy + 2)], 
                     fill=(255, 255, 255, 230))
        # Torch handle
        draw.rectangle([(cx - 3, cy + 2), (cx + 3, cy + 14)], fill=(255, 255, 255, 230))
        
        # Right button (camera) - dark rounded square
        right_x = bar_width - 35 - button_size
        draw.rounded_rectangle(
            [(right_x, button_y), (right_x + button_size, button_y + button_size)],
            radius=14,
            fill=(50, 50, 50, 200)
        )
        # Camera icon - body and lens
        cx, cy = right_x + button_size // 2, button_y + button_size // 2
        # Camera body
        draw.rounded_rectangle(
            [(cx - 14, cy - 6), (cx + 14, cy + 10)],
            radius=3,
            outline=(255, 255, 255, 230),
            width=2
        )
        # Camera lens (circle)
        draw.ellipse([(cx - 6, cy - 4), (cx + 6, cy + 8)], outline=(255, 255, 255, 230), width=2)
        # Camera viewfinder bump
        draw.rectangle([(cx - 4, cy - 10), (cx + 4, cy - 6)], fill=(255, 255, 255, 230))
        
        # Center hint text
        hint_text = "Swipe up to open"
        hint_bbox = draw.textbbox((0, 0), hint_text, font=font_hint)
        hint_width = hint_bbox[2] - hint_bbox[0]
        draw.text((bar_width // 2 - hint_width // 2, button_y + 60), hint_text, 
                 font=font_hint, fill=(255, 255, 255, 120))
        
        # Bottom home indicator line (thicker, more visible)
        line_width = 134
        line_height = 5
        line_x = (bar_width - line_width) // 2
        draw.rounded_rectangle(
            [(line_x, button_y + 95), (line_x + line_width, button_y + 95 + line_height)],
            radius=3,
            fill=(255, 255, 255, 200)
        )
        
        return np.array(img)
    
    def _create_calendar_overlay(self) -> np.ndarray:
        """Create calendar overlay - Hari, Tanggal Masehi, Tanggal Hijriah"""
        cal = self._get_calendar_info()
        
        # Create canvas
        cal_width = self.width
        cal_height = 140
        img = Image.new('RGBA', (cal_width, cal_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Fonts
        font_day = self._get_font(32)        # Hari (Jumat)
        font_masehi = self._get_font(24)     # Tanggal Masehi
        font_hijri = self._get_font(20)      # Tanggal Hijriah
        
        # Helper function to draw text with soft shadow
        def draw_text_shadow(pos, text, font, color=(255, 255, 255, 255)):
            x, y = pos
            shadow_color = (0, 0, 0, 60)
            draw.text((x + 2, y + 2), text, font=font, fill=shadow_color)
            draw.text((x, y), text, font=font, fill=color)
        
        center_x = cal_width // 2
        
        # Line 1: Hari (Jumat)
        day_text = cal['day_id']
        day_bbox = draw.textbbox((0, 0), day_text, font=font_day)
        day_width = day_bbox[2] - day_bbox[0]
        draw_text_shadow((center_x - day_width // 2, 10), day_text, font_day)
        
        # Line 2: Tanggal Masehi (5 Desember 2025)
        masehi_text = f"{cal['masehi_day']} {cal['masehi_month']} {cal['masehi_year']}"
        masehi_bbox = draw.textbbox((0, 0), masehi_text, font=font_masehi)
        masehi_width = masehi_bbox[2] - masehi_bbox[0]
        draw_text_shadow((center_x - masehi_width // 2, 50), masehi_text, font_masehi)
        
        # Line 3: Tanggal Hijriah (5 Jumadil Akhir 1447 H)
        hijri_text = f"{cal['hijri_day']} {cal['hijri_month']} {cal['hijri_year']} H"
        hijri_bbox = draw.textbbox((0, 0), hijri_text, font=font_hijri)
        hijri_width = hijri_bbox[2] - hijri_bbox[0]
        draw_text_shadow((center_x - hijri_width // 2, 90), hijri_text, font_hijri, (200, 200, 200, 255))
        
        return np.array(img)

    
    def _wrap_text_pil(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
        """Wrap text to fit within max_width using PIL"""
        words = text.split()
        lines = []
        current_line = []
        
        dummy_img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def _calculate_text_timing(self, audio_duration: float, text_arab: str, text_translation: str) -> TextTiming:
        """
        Calculate synchronized timing for text display based on audio duration.
        
        Uses AudioSyncService to determine when Arabic text and translation
        should appear and fade in/out.
        
        Args:
            audio_duration: Duration of audio in seconds
            text_arab: Arabic text
            text_translation: Translation text
            
        Returns:
            TextTiming object with calculated timings
        """
        return self.audio_sync.calculate_text_timing(
            audio_duration=audio_duration,
            text_arab=text_arab,
            text_translation=text_translation
        )

    def _split_text_into_segments(self, text: str, num_segments: int = 3) -> list:
        """
        Split text into segments for gradual display.
        
        Args:
            text: Text to split
            num_segments: Number of segments to create
            
        Returns:
            List of text segments
        """
        words = text.split()
        if len(words) <= num_segments:
            return [text]  # Too short to split
        
        # Calculate words per segment
        words_per_segment = len(words) // num_segments
        remainder = len(words) % num_segments
        
        segments = []
        start_idx = 0
        
        for i in range(num_segments):
            # Add extra word to earlier segments if there's remainder
            extra = 1 if i < remainder else 0
            end_idx = start_idx + words_per_segment + extra
            
            segment_words = words[start_idx:end_idx]
            if segment_words:
                segments.append(' '.join(segment_words))
            
            start_idx = end_idx
        
        return segments

    def _create_word_timed_clips(
        self,
        text_arab: str,
        word_timings: list,
        video_duration: float,
        base_y: int,
        fontsize: int = 56
    ) -> list:
        """
        Create text clips that appear word by word based on Quran.com timestamps.
        
        Args:
            text_arab: Full Arabic text
            word_timings: List of word timing dicts from Quran.com API
            video_duration: Total video duration
            base_y: Base Y position for text
            fontsize: Font size
            
        Returns:
            List of ImageClip objects
        """
        if not word_timings:
            return None
        
        clips = []
        words = text_arab.split()
        fade_duration = 0.2  # Faster fade for better sync
        
        # Group words into lines (max ~4 words per line for bigger text)
        words_per_line = min(4, max(2, len(words) // 3))
        lines = []
        current_line = []
        
        for i, word in enumerate(words):
            current_line.append((i, word))
            if len(current_line) >= words_per_line:
                lines.append(current_line)
                current_line = []
        if current_line:
            lines.append(current_line)
        
        # Calculate line heights (bigger spacing for larger font)
        line_height = fontsize + 30
        total_height = len(lines) * line_height
        start_y = base_y - total_height // 2
        
        # Create clips for each line
        for line_idx, line_words in enumerate(lines):
            # Get timing for this line (use first word's start time)
            first_word_idx = line_words[0][0]
            
            # Find timing for first word in this line
            line_start_ms = 0
            if first_word_idx < len(word_timings):
                line_start_ms = word_timings[first_word_idx].get("start_ms", 0)
            
            # Convert to seconds and subtract small offset for better sync
            # Text should appear slightly before audio for better perception
            line_start = max(0, (line_start_ms / 1000.0) - 0.1)
            
            # Create text for this line
            line_text = " ".join([w[1] for w in line_words])
            line_img = self._create_aesthetic_text(line_text, fontsize=fontsize, color='white', arabic=True)
            
            # Calculate clip timing
            clip_duration = video_duration - line_start
            if clip_duration <= 0:
                continue
            
            # Create clip
            line_clip = ImageClip(line_img).set_duration(clip_duration)
            line_clip = line_clip.set_start(line_start)
            line_clip = line_clip.set_position(('center', start_y + line_idx * line_height))
            line_clip = line_clip.crossfadein(fade_duration)
            
            clips.append(line_clip)
        
        return clips if clips else None

    def _create_segment_clips(
        self,
        text: str,
        audio_duration: float,
        base_y: int,
        fontsize: int = 52,
        arabic: bool = True,
        num_segments: int = 3
    ) -> list:
        """
        Create multiple text clips that appear segment by segment.
        
        Args:
            text: Full text to display
            audio_duration: Total audio duration
            base_y: Base Y position for text
            fontsize: Font size
            arabic: Whether text is Arabic
            num_segments: Number of segments
            
        Returns:
            List of ImageClip objects
        """
        segments = self._split_text_into_segments(text, num_segments)
        if len(segments) <= 1:
            # Single segment, use normal display
            return None
        
        clips = []
        fade_duration = 0.5
        
        # Calculate timing for each segment
        # Reserve 80% of audio for Arabic segments, last 20% for all visible
        arab_display_time = audio_duration * 0.8
        segment_duration = arab_display_time / len(segments)
        
        # Calculate vertical spacing
        segment_heights = []
        for seg_text in segments:
            seg_img = self._create_aesthetic_text(seg_text, fontsize=fontsize, color='white', arabic=arabic)
            segment_heights.append(seg_img.shape[0])
        
        total_height = sum(segment_heights) + (len(segments) - 1) * 15  # 15px gap between segments
        
        # Center vertically around base_y
        current_y = base_y - total_height // 2 + segment_heights[0] // 2
        
        for i, seg_text in enumerate(segments):
            seg_img = self._create_aesthetic_text(seg_text, fontsize=fontsize, color='white', arabic=arabic)
            
            # Calculate timing for this segment
            seg_start = i * segment_duration
            seg_end = audio_duration  # All segments stay until end
            
            # Create clip
            clip_duration = seg_end - seg_start
            seg_clip = ImageClip(seg_img).set_duration(clip_duration)
            seg_clip = seg_clip.set_start(seg_start)
            seg_clip = seg_clip.set_position(('center', current_y))
            seg_clip = seg_clip.crossfadein(fade_duration)
            seg_clip = seg_clip.crossfadeout(fade_duration)
            
            clips.append(seg_clip)
            
            # Move to next position
            current_y += segment_heights[i] + 15
        
        return clips

    async def generate_video(
        self,
        background_path: str,
        audio_path: str,
        text_arab: str,
        text_translation: str,
        surah_name: str,
        ayat_number: int,
        word_timings: list = None
    ) -> Dict[str, Any]:
        """Generate aesthetic wallpaper-style video with background and text overlay synchronized with audio"""
        
        output_filename = f"quran_{surah_name}_{ayat_number}_{uuid.uuid4().hex[:8]}.mp4"
        output_path = self.output_dir / output_filename
        
        try:
            # Load background video
            video = VideoFileClip(background_path)
            
            # Load audio
            audio = AudioFileClip(audio_path)
            audio_duration = audio.duration
            
            # Calculate video duration (minimum 10 seconds or audio length)
            video_duration = max(audio_duration, self.min_video_duration)
            
            # Calculate synchronized text timing based on audio
            text_timing = self._calculate_text_timing(audio_duration, text_arab, text_translation)
            
            # Store word timings for use in clip creation
            self._current_word_timings = word_timings
            
            # Resize and crop video to 9:16
            video = self._resize_to_portrait(video)
            
            # Loop or trim video to match duration
            if video.duration < video_duration:
                video = video.loop(duration=video_duration)
            else:
                video = video.subclip(0, video_duration)
            
            # Darken the background slightly for text readability
            video = video.fl_image(self._darken_frame)
            
            # Create iPhone lock screen elements
            status_bar_img = self._create_status_bar()
            calendar_img = self._create_calendar_overlay()
            bottom_bar_img = self._create_bottom_bar()
            
            # Position content in center area (between calendar and bottom bar)
            content_start = int(self.height * 0.28)
            content_end = self.height - 150
            
            # Arabic text position (centered in content area)
            arab_y = content_start + 180
            
            # Try to use word timings from Quran.com API for accurate sync
            arab_segment_clips = None
            if word_timings and len(word_timings) > 0:
                # Use word-level timestamps for accurate sync with qari
                # Font size 56 for better readability
                arab_segment_clips = self._create_word_timed_clips(
                    text_arab=text_arab,
                    word_timings=word_timings,
                    video_duration=video_duration,
                    base_y=arab_y,
                    fontsize=56
                )
            
            # Fallback to segment-based display if no word timings
            if not arab_segment_clips:
                arab_words = len(text_arab.split())
                num_segments = min(4, max(2, arab_words // 4))
                arab_segment_clips = self._create_segment_clips(
                    text=text_arab,
                    audio_duration=audio_duration,
                    base_y=arab_y,
                    fontsize=56,
                    arabic=True,
                    num_segments=num_segments
                )
            
            # Create translation text (appears after Arabic segments)
            trans_img = self._create_aesthetic_text(text_translation, fontsize=28, color='white', italic_style=True)
            trans_height = trans_img.shape[0]
            
            # Create surah reference
            surah_ref = f"— QS. {surah_name}: {ayat_number}"
            ref_img = self._create_aesthetic_text(surah_ref, fontsize=22, color='#D4C4A8')
            ref_height = ref_img.shape[0]
            
            # Position translation and reference at bottom area
            trans_y = content_end - trans_height - ref_height - 40
            ref_y = trans_y + trans_height + 15
            
            # Translation appears after 70% of audio
            trans_start = audio_duration * 0.7
            trans_fade_in = 0.5
            fade_out_duration = 0.5
            
            # Translation clip
            trans_clip_duration = video_duration - trans_start
            trans_clip = ImageClip(trans_img).set_duration(trans_clip_duration)
            trans_clip = trans_clip.set_start(trans_start)
            trans_clip = trans_clip.set_position(('center', trans_y))
            trans_clip = trans_clip.crossfadein(trans_fade_in)
            trans_clip = trans_clip.crossfadeout(fade_out_duration)
            
            # Reference clip - appears shortly after translation
            ref_start = min(trans_start + 0.3, video_duration - 1.0)
            ref_clip_duration = video_duration - ref_start
            ref_clip = ImageClip(ref_img).set_duration(ref_clip_duration)
            ref_clip = ref_clip.set_start(ref_start)
            ref_clip = ref_clip.set_position(('center', ref_y))
            ref_clip = ref_clip.crossfadein(trans_fade_in)
            ref_clip = ref_clip.crossfadeout(fade_out_duration)
            
            # Create status bar clip (top right)
            status_bar_clip = ImageClip(status_bar_img).set_duration(video_duration)
            status_bar_clip = status_bar_clip.set_position(('center', 10))
            status_bar_clip = status_bar_clip.crossfadein(self.fade_duration)
            
            # Create calendar clip - positioned at top
            calendar_clip = ImageClip(calendar_img).set_duration(video_duration)
            calendar_clip = calendar_clip.set_position(('center', 60))
            calendar_clip = calendar_clip.crossfadein(self.fade_duration)
            
            # Create bottom bar clip
            bottom_bar_clip = ImageClip(bottom_bar_img).set_duration(video_duration)
            bottom_bar_clip = bottom_bar_clip.set_position(('center', self.height - 100))
            bottom_bar_clip = bottom_bar_clip.crossfadein(self.fade_duration)
            
            # Create list of clips
            clips = [video, status_bar_clip, calendar_clip]
            
            # Add Arabic segment clips (segment by segment display)
            if arab_segment_clips:
                clips.extend(arab_segment_clips)
            else:
                # Fallback: create single Arabic clip if segmentation failed
                arab_img = self._create_aesthetic_text(text_arab, fontsize=48, color='white', arabic=True)
                arab_clip = ImageClip(arab_img).set_duration(video_duration)
                arab_clip = arab_clip.set_position(('center', arab_y))
                arab_clip = arab_clip.crossfadein(0.5)
                arab_clip = arab_clip.crossfadeout(0.5)
                clips.append(arab_clip)
            
            # Add translation and reference clips
            clips.extend([trans_clip, ref_clip, bottom_bar_clip])
            
            # Add watermark
            watermark_clip = self._create_watermark_clip(video_duration)
            clips.append(watermark_clip)
            
            # Composite all clips
            final = CompositeVideoClip(clips)
            
            # Set audio (no fade to avoid crackling at the end)
            final = final.set_audio(audio)
            
            # Only fade in video, not fade out (to avoid audio crackling)
            final = final.crossfadein(self.fade_duration)
            
            # Write output with better audio settings
            final.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                audio_bitrate='192k',
                threads=4,
                preset='medium',
                logger=None
            )
            
            # Get file info
            file_size = os.path.getsize(output_path)
            
            # Cleanup
            video.close()
            audio.close()
            final.close()
            
            return {
                "output_file": str(output_path),
                "filename": output_filename,
                "duration": video_duration,
                "file_size": file_size
            }
            
        except Exception as e:
            raise Exception(f"Video generation failed: {str(e)}")

    def _create_logo_clip(self, duration: float, y_position: int) -> Optional[ImageClip]:
        """Create logo clip with white color and transparent background"""
        if not self.logo_path.exists():
            print(f"Logo not found at {self.logo_path}")
            return None
        
        try:
            # Load logo
            logo = Image.open(self.logo_path).convert('RGBA')
            
            # Resize logo to fit (max width 150px, maintain aspect ratio)
            max_logo_width = 150
            if logo.width > max_logo_width:
                ratio = max_logo_width / logo.width
                new_size = (max_logo_width, int(logo.height * ratio))
                logo = logo.resize(new_size, Image.LANCZOS)
            
            # Get pixel data
            logo_data = np.array(logo)
            
            # Create mask based on non-white/non-transparent pixels
            # If logo has alpha channel, use it
            if logo_data.shape[2] == 4:
                alpha = logo_data[:, :, 3]
            else:
                # Create alpha from non-white pixels
                r, g, b = logo_data[:, :, 0], logo_data[:, :, 1], logo_data[:, :, 2]
                # Pixels that are not pure white (255,255,255) become visible
                alpha = 255 - np.minimum(np.minimum(r, g), b)
            
            # Create white logo with proper alpha
            white_logo = np.zeros((logo_data.shape[0], logo_data.shape[1], 4), dtype=np.uint8)
            white_logo[:, :, 0] = 255  # R
            white_logo[:, :, 1] = 255  # G
            white_logo[:, :, 2] = 255  # B
            white_logo[:, :, 3] = alpha  # A
            
            # Create ImageClip with mask
            logo_clip = ImageClip(white_logo).set_duration(duration)
            logo_clip = logo_clip.set_position(('center', y_position))
            
            return logo_clip
            
        except Exception as e:
            print(f"Error loading logo: {e}")
            return None
    
    def _create_watermark_clip(self, duration: float) -> ImageClip:
        """Create minimalist text watermark (small, low opacity, bottom center)"""
        font = self._get_font(20)  # Small font size
        
        # Calculate text size
        dummy_img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        bbox = draw.textbbox((0, 0), self.watermark_text, font=font)
        text_width = bbox[2] - bbox[0] + 20
        text_height = bbox[3] - bbox[1] + 10
        
        # Create image with transparent background
        img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Calculate alpha based on opacity (35% = 89 out of 255)
        alpha = int(255 * self.watermark_opacity)
        
        # Draw watermark text (white with low opacity)
        draw.text((10, 5), self.watermark_text, font=font, fill=(255, 255, 255, alpha))
        
        # Convert to numpy array
        watermark_array = np.array(img)
        
        # Create ImageClip positioned at bottom center
        watermark_clip = ImageClip(watermark_array).set_duration(duration)
        watermark_y = self.height - 80  # 80px from bottom
        watermark_clip = watermark_clip.set_position(('center', watermark_y))
        
        return watermark_clip
    
    def _darken_frame(self, frame: np.ndarray) -> np.ndarray:
        """Darken video frame slightly for text readability while keeping aesthetic"""
        # Reduce brightness to configured level (default 55%)
        darkened = (frame * self.bg_darken).astype(np.uint8)
        return darkened
    
    def _resize_to_portrait(self, video: VideoFileClip) -> VideoFileClip:
        """Resize video to 9:16 portrait format"""
        target_ratio = self.width / self.height  # 9:16 = 0.5625
        current_ratio = video.w / video.h
        
        if current_ratio > target_ratio:
            # Video is wider, crop sides
            new_width = int(video.h * target_ratio)
            x_center = video.w / 2
            video = video.crop(
                x1=x_center - new_width/2,
                x2=x_center + new_width/2
            )
        else:
            # Video is taller, crop top/bottom
            new_height = int(video.w / target_ratio)
            y_center = video.h / 2
            video = video.crop(
                y1=y_center - new_height/2,
                y2=y_center + new_height/2
            )
        
        return video.resize((self.width, self.height))
