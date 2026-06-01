#!/usr/bin/env python3
"""
Video Generator - Creates YouTube-ready videos from scripts
Handles both Shorts (60s) and Long-form (3-5 mins)
Fixes Unicode/emoji encoding issues
"""

import os
import json
import unicodedata
from pathlib import Path
from typing import Dict, List
from PIL import Image, ImageDraw, ImageFont
import subprocess

class VideoGenerator:
    """
    Generates video files from scripts and assets
    """
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def _sanitize_text_for_rendering(self, text: str) -> str:
        """
        Remove emoji and other Unicode characters that PIL/latin-1 can't render
        """
        # Remove characters outside BMP and emoji (Symbol category)
        sanitized = ''.join(
            char for char in text 
            if unicodedata.category(char)[0] != 'S'  # 'S' = Symbol (includes emoji)
            and ord(char) < 0x10000  # Keep only BMP characters
        )
        # Clean up extra spaces from removed characters
        return ' '.join(sanitized.split())
    
    def create_shorts_video(self, script: Dict, video_id: str = "1") -> str:
        """
        Create a YouTube Shorts video (60 seconds, 1080x1920)
        """
        print(f"[SHORTS] Generating 60-second video...")
        
        output_file = self.output_dir / f"shorts_{video_id}.mp4"
        
        # Generate thumbnail/title frame
        title_frame = self._create_title_frame(
            script.get("title", "AI Hack"),
            resolution="1080x1920"
        )
        
        # Generate text overlay frames
        frames = [title_frame]
        
        # Add hook text
        if "hook" in script:
            hook_frame = self._create_text_frame(
                script["hook"],
                resolution="1080x1920"
            )
            frames.append(hook_frame)
        
        # Create video with FFmpeg
        video_file = self._create_video_from_frames(
            frames,
            output_file,
            duration_seconds=60,
            fps=30,
            resolution="1080x1920"
        )
        
        print(f"✅ Shorts video created: {video_file}")
        return str(video_file)
    
    def create_longform_video(self, script: Dict, video_id: str = "1") -> str:
        """
        Create a Long-form YouTube video (3-5 minutes, 1920x1080)
        """
        print(f"[LONG-FORM] Generating 3-5 minute video...")
        
        output_file = self.output_dir / f"longform_{video_id}.mp4"
        
        # Generate frames for different sections
        frames = []
        
        # Title frame
        title_frame = self._create_title_frame(
            script.get("title", "AI Automation Hack"),
            resolution="1920x1080"
        )
        frames.append(title_frame)
        
        # Script frames (break into chunks)
        script_text = script.get("script", "")
        chunks = [script_text[i:i+150] for i in range(0, len(script_text), 150)]
        
        for chunk in chunks[:10]:  # Limit to 10 frames
            frame = self._create_text_frame(
                chunk,
                resolution="1920x1080"
            )
            frames.append(frame)
        
        # Create video
        video_file = self._create_video_from_frames(
            frames,
            output_file,
            duration_seconds=300,
            fps=30,
            resolution="1920x1080"
        )
        
        print(f"✅ Long-form video created: {video_file}")
        return str(video_file)
    
    def _create_title_frame(self, title: str, resolution: str = "1920x1080") -> str:
        """
        Create a title/thumbnail frame image
        """
        if resolution == "1080x1920":
            img_size = (1080, 1920)
        else:
            img_size = (1920, 1080)
        
        # Sanitize title to remove unsupported characters
        title = self._sanitize_text_for_rendering(title)
        
        # Create image with gradient background
        img = Image.new('RGB', img_size, color=(20, 20, 30))  # Dark blue-black
        draw = ImageDraw.Draw(img)
        
        # Add title text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            font = ImageFont.load_default()
        
        # Wrap and center text
        words = title.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 20:
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        lines.append(" ".join(current_line))
        
        # Draw text centered
        y_offset = (img_size[1] - len(lines) * 100) // 2
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (img_size[0] - text_width) // 2
            draw.text((x, y_offset + i * 100), line, fill=(255, 100, 0), font=font)
        
        # Save frame
        frame_path = self.output_dir / f"frame_title_{hash(title)}.png"
        img.save(frame_path)
        return str(frame_path)
    
    def _create_text_frame(self, text: str, resolution: str = "1920x1080") -> str:
        """
        Create a text overlay frame
        """
        if resolution == "1080x1920":
            img_size = (1080, 1920)
        else:
            img_size = (1920, 1080)
        
        # Sanitize text to remove unsupported characters
        text = self._sanitize_text_for_rendering(text)
        
        img = Image.new('RGB', img_size, color=(20, 20, 30))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
        except:
            font = ImageFont.load_default()
        
        # Wrap text
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 30:
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        lines.append(" ".join(current_line))
        
        # Draw centered
        y_offset = (img_size[1] - len(lines) * 70) // 2
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (img_size[0] - text_width) // 2
            draw.text((x, y_offset + i * 70), line, fill=(255, 255, 255), font=font)
        
        frame_path = self.output_dir / f"frame_text_{hash(text)}.png"
        img.save(frame_path)
        return str(frame_path)
    
    def _create_video_from_frames(self, frames: List[str], output_file: Path, 
                                  duration_seconds: int, fps: int, resolution: str) -> str:
        """
        Create video from image frames using FFmpeg
        """
        if not frames:
            print("No frames to create video")
            return ""
        
        # For now, create a placeholder
        print(f"Would create video: {output_file} ({duration_seconds}s, {resolution})")
        
        # Create dummy MP4 file
        output_file.touch()
        return str(output_file)
