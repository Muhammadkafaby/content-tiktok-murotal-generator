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

from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
from api.config import VIDEOS_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS


class VideoGenerator:
    def __init__(self):
        self.output_dir = VIDEOS_DIR
        self.width = VIDEO_WIDTH
        self.height = VIDEO_HEIGHT
        self.fps = VIDEO_FPS
        # Try to find a suitable font
        self.font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        ]
    
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get available font"""
        for font_path in self.font_paths:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        # Fallback to default
        return ImageFont.load_default()
    
    def _create_text_image(
        self,
        text: str,
        fontsize: int,
        color: str = 'white',
        max_width: int = None
    ) -> np.ndarray:
        """Create text image using PIL (no ImageMagick needed)"""
        if max_width is None:
            max_width = self.width - 100
        
        font = self._get_font(fontsize)
        
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
            
            # Trim or loop video to match audio duration
            if video.duration < audio_duration:
                video = video.loop(duration=audio_duration)
            else:
                video = video.subclip(0, audio_duration)
            
            # Create text overlays using PIL (no ImageMagick)
            arab_img = self._create_text_image(text_arab, fontsize=42, color='white')
            trans_img = self._create_text_image(text_translation, fontsize=28, color='white')
            
            # Create ImageClips from PIL images
            arab_clip = ImageClip(arab_img).set_duration(audio_duration)
            arab_clip = arab_clip.set_position(('center', 0.30), relative=True)
            
            trans_clip = ImageClip(trans_img).set_duration(audio_duration)
            trans_clip = trans_clip.set_position(('center', 0.65), relative=True)
            
            # Composite video
            final = CompositeVideoClip([video, arab_clip, trans_clip])
            final = final.set_audio(audio)
            
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
            
            return {
                "output_file": str(output_path),
                "filename": output_filename,
                "duration": audio_duration,
                "file_size": file_size
            }
            
        except Exception as e:
            raise Exception(f"Video generation failed: {str(e)}")

    
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
