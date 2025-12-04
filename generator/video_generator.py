import os
import uuid
import tempfile
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

# Fix for Pillow 10+ compatibility with moviepy
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
from api.config import VIDEOS_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, DATA_DIR
from generator.hook_generator import HookGenerator


class VideoGenerator:
    def __init__(self):
        self.output_dir = VIDEOS_DIR
        self.width = VIDEO_WIDTH
        self.height = VIDEO_HEIGHT
        self.fps = VIDEO_FPS
        self.logo_path = DATA_DIR / "assets" / "logo.png"
        self.hook_generator = HookGenerator()
        self.hook_duration = 1.5  # Hook duration in seconds
        self.cta_duration = 2.0   # CTA outro duration in seconds
        self.cta_texts = [
            "Follow untuk ayat harian 🤲",
            "Like & Follow untuk lebih banyak 💫",
            "Bagikan kebaikan ini ✨",
            "Follow untuk inspirasi Quran 📖",
        ]
        # Font paths for regular text
        self.font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        ]
        # Font paths for Arabic text
        self.arabic_font_paths = [
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
    
    async def generate_video(
        self,
        background_path: str,
        audio_path: str,
        text_arab: str,
        text_translation: str,
        surah_name: str,
        ayat_number: int
    ) -> Dict[str, Any]:
        """Generate video with background, audio, and text overlay"""
        
        output_filename = f"quran_{surah_name}_{ayat_number}_{uuid.uuid4().hex[:8]}.mp4"
        output_path = self.output_dir / output_filename
        
        try:
            # Load background video
            video = VideoFileClip(background_path)
            
            # Load audio
            audio = AudioFileClip(audio_path)
            audio_duration = audio.duration
            
            # Resize and crop video to 9:16
            video = self._resize_to_portrait(video)
            
            # Generate hook text
            hook_text = self.hook_generator.get_hook(text_translation, surah_name)
            
            # Create hook intro clip (before darkening main video)
            hook_clip = self._create_hook_clip(hook_text, video)
            
            # Total duration needed: hook + audio + cta
            total_duration = self.hook_duration + audio_duration + self.cta_duration
            if video.duration < total_duration:
                video = video.loop(duration=total_duration)
            else:
                video = video.subclip(0, total_duration)
            
            # Get main content portion (after hook, before CTA)
            main_video = video.subclip(self.hook_duration, self.hook_duration + audio_duration)
            
            # Darken the main video background (reduce brightness to 50%)
            main_video = main_video.fx(lambda clip: clip.fl_image(self._darken_frame))
            
            # Create text overlays using PIL (no ImageMagick)
            arab_img = self._create_text_image(text_arab, fontsize=48, color='white', arabic=True)
            trans_img = self._create_text_image(text_translation, fontsize=32, color='white')
            
            # Create surah reference text (QS: Surah Name: Ayat)
            surah_ref = f"QS. {surah_name}: {ayat_number}"
            ref_img = self._create_text_image(surah_ref, fontsize=28, color='#FFD700')  # Gold color
            
            # Get image heights for dynamic positioning
            arab_height = arab_img.shape[0]
            trans_height = trans_img.shape[0]
            ref_height = ref_img.shape[0]
            
            # Calculate dynamic positions based on content height
            # Margins: top 8%, bottom 15% (more space at bottom for ref)
            top_margin = int(self.height * 0.08)
            bottom_margin = int(self.height * 0.15)
            
            # Calculate spacing between elements
            total_content_height = arab_height + trans_height + ref_height
            available_height = self.height - top_margin - bottom_margin - total_content_height
            spacing = available_height // 4
            spacing = max(spacing, 25)  # Minimum 25px spacing
            
            # Position calculations (in pixels from top)
            arab_y = top_margin + spacing
            trans_y = arab_y + arab_height + spacing
            ref_y = trans_y + trans_height + spacing  # Reference right after translation
            
            # Create ImageClips with calculated positions
            arab_clip = ImageClip(arab_img).set_duration(audio_duration)
            arab_clip = arab_clip.set_position(('center', arab_y))
            
            trans_clip = ImageClip(trans_img).set_duration(audio_duration)
            trans_clip = trans_clip.set_position(('center', trans_y))
            
            ref_clip = ImageClip(ref_img).set_duration(audio_duration)
            ref_clip = ref_clip.set_position(('center', ref_y))
            
            # Create list of clips for main content
            main_clips = [main_video, arab_clip, trans_clip, ref_clip]
            
            # Add logo if exists
            logo_clip = self._create_logo_clip(audio_duration, ref_y + ref_height + 20)
            if logo_clip:
                main_clips.append(logo_clip)
            
            # Composite main content
            main_composite = CompositeVideoClip(main_clips)
            main_composite = main_composite.set_audio(audio)
            
            # Create CTA outro clip
            cta_clip = self._create_cta_clip(video)
            
            # Concatenate hook + main content + CTA
            final = concatenate_videoclips([hook_clip, main_composite, cta_clip])
            
            # Write output
            final.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
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
            hook_clip.close()
            main_composite.close()
            cta_clip.close()
            
            return {
                "output_file": str(output_path),
                "filename": output_filename,
                "duration": audio_duration,
                "file_size": file_size
            }
            
        except Exception as e:
            raise Exception(f"Video generation failed: {str(e)}")

    
    def _create_cta_clip(self, bg_video: VideoFileClip) -> CompositeVideoClip:
        """Create CTA outro clip (2 seconds)"""
        import random
        
        # Pick random CTA text
        cta_text = random.choice(self.cta_texts)
        
        # Create CTA text image
        cta_img = self._create_text_image(cta_text, fontsize=44, color='#FFFFFF')
        
        # Get end portion of background video for CTA
        start_time = max(0, bg_video.duration - self.cta_duration)
        cta_bg = bg_video.subclip(start_time, bg_video.duration)
        if cta_bg.duration < self.cta_duration:
            cta_bg = cta_bg.loop(duration=self.cta_duration)
        
        # Darken CTA background (45% brightness)
        cta_bg = cta_bg.fl_image(lambda frame: (frame * 0.45).astype(np.uint8))
        
        # Position CTA text in center
        cta_text_clip = ImageClip(cta_img).set_duration(self.cta_duration)
        cta_text_clip = cta_text_clip.set_position(('center', 'center'))
        
        # Add logo below CTA if exists
        clips = [cta_bg, cta_text_clip]
        
        if self.logo_path.exists():
            logo_clip = self._create_logo_clip(self.cta_duration, int(self.height * 0.65))
            if logo_clip:
                clips.append(logo_clip)
        
        # Composite CTA
        cta_composite = CompositeVideoClip(clips)
        
        return cta_composite
    
    def _create_hook_clip(self, hook_text: str, bg_video: VideoFileClip) -> CompositeVideoClip:
        """Create hook intro clip (1.5 seconds)"""
        # Create hook text image with larger font
        hook_img = self._create_text_image(hook_text, fontsize=56, color='#FFFFFF')
        
        # Get a portion of background video for hook
        hook_bg = bg_video.subclip(0, min(self.hook_duration, bg_video.duration))
        if hook_bg.duration < self.hook_duration:
            hook_bg = hook_bg.loop(duration=self.hook_duration)
        else:
            hook_bg = hook_bg.subclip(0, self.hook_duration)
        
        # Darken hook background more (40% brightness)
        hook_bg = hook_bg.fl_image(lambda frame: (frame * 0.4).astype(np.uint8))
        
        # Position hook text in center
        hook_clip = ImageClip(hook_img).set_duration(self.hook_duration)
        hook_clip = hook_clip.set_position(('center', 'center'))
        
        # Composite hook
        hook_composite = CompositeVideoClip([hook_bg, hook_clip])
        
        return hook_composite
    
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
            
            # Convert to white (keep alpha channel)
            logo_data = logo.getdata()
            new_data = []
            for item in logo_data:
                # If pixel is not fully transparent, make it white
                if item[3] > 0:
                    new_data.append((255, 255, 255, item[3]))
                else:
                    new_data.append(item)
            logo.putdata(new_data)
            
            # Convert to numpy array
            logo_array = np.array(logo)
            
            # Create ImageClip
            logo_clip = ImageClip(logo_array).set_duration(duration)
            logo_clip = logo_clip.set_position(('center', y_position))
            
            return logo_clip
            
        except Exception as e:
            print(f"Error loading logo: {e}")
            return None
    
    def _darken_frame(self, frame: np.ndarray) -> np.ndarray:
        """Darken video frame by reducing brightness"""
        # Reduce brightness to 50% (0.5 multiplier)
        darkened = (frame * 0.5).astype(np.uint8)
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
