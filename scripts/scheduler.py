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
        print(f"\n🎬 Scheduling {self.videos_per_day} videos daily at {self.upload_time}")
        
        # Schedule upload at specified time
        schedule.every().day.at(self.upload_time).do(self.generate_and_upload_video)
        
        print("✅ Scheduler started. Videos will upload daily.")
        print("Press Ctrl+C to stop.\n")
        
        # Keep scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def generate_and_upload_video(self):
        """
        Main workflow: generate script -> create video -> upload to YouTube
        """
        print(f"\n📹 Generating video at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...\n")
        
        try:
            # Import generators
            from script_generator import ScriptGenerator
            from video_generator import VideoGenerator
            from uploader import YouTubeUploader
            
            # Step 1: Get prompt
            prompt, video_type, duration = self._get_next_prompt()
            print(f"Prompt: {prompt}")
            
            # Step 2: Generate script
            print("\n[1/4] Generating script...")
            generator = ScriptGenerator(api_provider="openai")
            script = generator.generate_script(prompt, video_type, duration)
            
            # Step 3: Create videos
            print("\n[2/4] Creating videos...")
            video_gen = VideoGenerator()
            
            video_id = datetime.now().strftime("%Y%m%d%H%M%S")
            
            if "short" in video_type.lower():
                shorts_file = video_gen.create_shorts_video(script, video_id)
            
            longform_file = video_gen.create_longform_video(script, video_id)
            
            # Step 4: Upload to YouTube
            print("\n[3/4] Uploading to YouTube...")
            uploader = YouTubeUploader()
            
            metadata = {
                "title": script.get("title", "AI Hack"),
                "description": script.get("description", "Check out this AI hack!"),
                "tags": script.get("tags", ["AI", "automation"]),
                "category_id": "28"
            }
            
            video_id = uploader.upload_video(longform_file, metadata, visibility="public")
            
            if video_id:
                print(f"\n✅ Successfully uploaded! Video ID: {video_id}")
                self._log_upload(prompt, video_id, longform_file)
            else:
                print("❌ Upload failed")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
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
