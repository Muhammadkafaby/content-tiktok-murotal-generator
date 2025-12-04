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
            "Ikuti untuk ayat lainnya.",
            "Bagikan ayat ini sebagai kebaikan.",
            "Sebarkan kebaikan, ikuti kami.",
            "Simpan dan bagikan ayat ini.",
        ]
        self.ai_api_url = "https://api.elrayyxml.web.id/api/ai/chatgpt"
        self.watermark_text = "@ruang.ayat"
        self.watermark_opacity = 0.35  # 35% opacity
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
            logo_y = ref_y + ref_height + spacing  # Logo below surah reference
            
            # Create ImageClips with calculated positions
            arab_clip = ImageClip(arab_img).set_duration(audio_duration)
            arab_clip = arab_clip.set_position(('center', arab_y))
            
            trans_clip = ImageClip(trans_img).set_duration(audio_duration)
            trans_clip = trans_clip.set_position(('center', trans_y))
            
            ref_clip = ImageClip(ref_img).set_duration(audio_duration)
            ref_clip = ref_clip.set_position(('center', ref_y))
            
            # Create list of clips for main content
            main_clips = [main_video, arab_clip, trans_clip, ref_clip]
            
            # Add watermark
            watermark_clip = self._create_watermark_clip(audio_duration)
            main_clips.append(watermark_clip)
            
            # Composite main content
            main_composite = CompositeVideoClip(main_clips)
            main_composite = main_composite.set_audio(audio)
            
            # Create CTA outro clip with AI-generated closing
            cta_clip = self._create_cta_clip(video, text_translation)
            
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

    
    def _generate_cta_with_ai(self, translation: str) -> Optional[str]:
        """Generate CTA closing using AI API"""
        import urllib.parse
        import httpx
        
        prompt = f"""Buatkan 1 kalimat penutup video TikTok Islami yang mengajak penonton untuk follow/bagikan. Harus relevan dengan ayat berikut:

"{translation}"

ATURAN:
1. Maksimal 8 kata
2. Bahasa Indonesia
3. JANGAN pakai emoji
4. Ajak follow atau bagikan
5. Relevan dengan isi ayat

Contoh:
- "Ikuti untuk ayat lainnya."
- "Bagikan ayat ini sebagai kebaikan."
- "Sebarkan kebaikan, ikuti kami."

Tulis HANYA kalimat penutupnya:"""

        try:
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"{self.ai_api_url}?text={encoded_prompt}"
            
            response = httpx.get(url, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("result"):
                    cta = data["result"].strip().strip('"\'')
                    if len(cta) <= 60:
                        return cta
            return None
        except Exception as e:
            print(f"AI CTA generation failed: {e}")
            return None
    
    def _create_cta_clip(self, bg_video: VideoFileClip, translation: str = None) -> CompositeVideoClip:
        """Create CTA outro clip (2 seconds)"""
        import random
        
        # Try AI first if translation provided
        cta_text = None
        if translation:
            cta_text = self._generate_cta_with_ai(translation)
        
        # Fallback to random CTA
        if not cta_text:
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
        
        # Add watermark to CTA
        watermark_clip = self._create_watermark_clip(self.cta_duration)
        
        # Composite CTA with watermark
        cta_composite = CompositeVideoClip([cta_bg, cta_text_clip, watermark_clip])
        
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
        
        # Add watermark to hook
        watermark_clip = self._create_watermark_clip(self.hook_duration)
        
        # Composite hook with watermark
        hook_composite = CompositeVideoClip([hook_bg, hook_clip, watermark_clip])
        
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
