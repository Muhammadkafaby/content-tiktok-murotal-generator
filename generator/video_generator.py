import os
import uuid
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from api.config import VIDEOS_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS


class VideoGenerator:
    def __init__(self):
        self.output_dir = VIDEOS_DIR
        self.width = VIDEO_WIDTH
        self.height = VIDEO_HEIGHT
        self.fps = VIDEO_FPS
    
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
            
            # Create text overlays
            arab_clip = self._create_text_clip(
                text_arab,
                fontsize=48,
                color='white',
                position=('center', 0.35),
                duration=audio_duration,
                font='Arial'  # TODO: Use Arabic font
            )
            
            trans_clip = self._create_text_clip(
                text_translation,
                fontsize=32,
                color='white',
                position=('center', 0.65),
                duration=audio_duration
            )
            
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
                preset='medium'
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
    
    def _create_text_clip(
        self,
        text: str,
        fontsize: int,
        color: str,
        position: tuple,
        duration: float,
        font: str = 'Arial'
    ) -> TextClip:
        """Create text clip with styling"""
        # Wrap long text
        max_chars = 40
        wrapped_text = self._wrap_text(text, max_chars)
        
        clip = TextClip(
            wrapped_text,
            fontsize=fontsize,
            color=color,
            font=font,
            method='caption',
            size=(self.width - 100, None),
            align='center'
        )
        
        clip = clip.set_position(position, relative=True)
        clip = clip.set_duration(duration)
        
        return clip
    
    def _wrap_text(self, text: str, max_chars: int) -> str:
        """Wrap text to multiple lines"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
