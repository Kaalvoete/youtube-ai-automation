#!/usr/bin/env python3
"""
Daily Scheduler - Automatically generates and uploads videos daily
"""

import os
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

from scripts.utils import create_video_pipeline

load_dotenv()

class VideoScheduler:
    """
    Schedules daily video generation and upload
    """
    
    def __init__(self):
        self.upload_time = os.getenv("DAILY_UPLOAD_TIME", "09:00")
        self.videos_per_day = int(os.getenv("VIDEOS_PER_DAY", "2"))
        self.prompt_file = "config/prompts.txt"
        self.current_prompt_index = 0
    
    def schedule_daily_uploads(self):
        """
        Schedule daily video generation and upload
        """
        print(f"\nScheduling {self.videos_per_day} videos daily at {self.upload_time}")
        
        # Schedule upload at specified time
        schedule.every().day.at(self.upload_time).do(self.generate_and_upload_video)
        
        print("Scheduler started. Videos will upload daily.")
        print("Press Ctrl+C to stop.\n")
        
        # Keep scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def generate_and_upload_video(self):
        """
        Main workflow: generate script -> create video -> upload to YouTube
        """
        print(f"\nGenerating video at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...\n")
        
        try:
            prompt, video_type, duration = self._get_next_prompt()
            print(f"Prompt: {prompt}")
            
            video_id = datetime.now().strftime("%Y%m%d%H%M%S")

            yt_video_id = create_video_pipeline(
                prompt=prompt,
                video_type=video_type,
                duration=duration,
                video_id=video_id,
                api_provider="openai",
                upload=True,
            )

            if yt_video_id:
                print(f"\nSuccessfully uploaded! Video ID: {yt_video_id}")
                self._log_upload(prompt, yt_video_id, f"output/longform_{video_id}.mp4")
            else:
                print("Upload failed")
        
        except Exception as e:
            print(f"Error: {e}")
    
    def _get_next_prompt(self) -> tuple:
        """
        Get next prompt from prompts.txt file
        """
        try:
            with open(self.prompt_file, 'r') as f:
                lines = [line.strip() for line in f.readlines() 
                        if line.strip() and not line.startswith('#')]
            
            if not lines:
                return ("AI Automation Hack", "tutorial", "5-min")
            
            # Cycle through prompts
            prompt_line = lines[self.current_prompt_index % len(lines)]
            self.current_prompt_index += 1
            
            # Parse format: "Type | Prompt | Duration"
            parts = [p.strip() for p in prompt_line.split('|')]
            
            video_type = parts[0] if len(parts) > 0 else "tutorial"
            prompt = parts[1] if len(parts) > 1 else "AI Hack"
            duration = parts[2] if len(parts) > 2 else "5-min"
            
            return (prompt, video_type.lower(), duration)
        
        except Exception as e:
            print(f"Error reading prompts: {e}")
            return ("AI Automation Hack", "tutorial", "5-min")
    
    def _log_upload(self, prompt: str, video_id: str, file_path: str):
        """
        Log uploaded video for tracking
        """
        log_file = "logs/upload_log.txt"
        Path("logs").mkdir(exist_ok=True)
        
        with open(log_file, 'a') as f:
            timestamp = datetime.now().isoformat()
            f.write(f"[{timestamp}] Prompt: {prompt}\n")
            f.write(f"Video ID: {video_id}\n")
            f.write(f"File: {file_path}\n")
            f.write("-" * 80 + "\n")
