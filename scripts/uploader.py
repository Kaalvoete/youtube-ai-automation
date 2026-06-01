#!/usr/bin/env python3
"""
YouTube Uploader - Automatically uploads videos to YouTube
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class YouTubeUploader:
    """
    Handles video uploads to YouTube with metadata
    """
    
    def __init__(self):
        self.channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
        self.setup_client()
    
    def setup_client(self):
        """Initialize YouTube API client"""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            
            self.youtube = build('youtube', 'v3')
            self.MediaFileUpload = MediaFileUpload
        except ImportError:
            print("Install: pip install google-api-python-client google-auth-oauthlib")
            self.youtube = None
    
    def upload_video(self, video_file: str, metadata: Dict, 
                     visibility: str = "public", made_for_kids: bool = False) -> Optional[str]:
        """
        Upload a video to YouTube
        """
        
        if not os.path.exists(video_file):
            print(f"Video file not found: {video_file}")
            return None
        
        if not self.youtube:
            print("YouTube client not initialized")
            return None
        
        try:
            body = {
                "snippet": {
                    "title": metadata.get("title", "New Video"),
                    "description": metadata.get("description", ""),
                    "tags": metadata.get("tags", []),
                    "categoryId": metadata.get("category_id", "28")
                },
                "status": {
                    "privacyStatus": visibility,
                    "madeForKids": made_for_kids
                }
            }
            
            media = self.MediaFileUpload(
                video_file,
                chunksize=-1,
                resumable=True,
                mimetype='video/mp4'
            )
            
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            response = request.execute()
            video_id = response['id']
            
            print(f"✅ Video uploaded successfully!")
            print(f"Video ID: {video_id}")
            print(f"URL: https://www.youtube.com/watch?v={video_id}")
            
            return video_id
        
        except Exception as e:
            print(f"Error uploading video: {e}")
            return None
    
    def schedule_upload(self, video_file: str, metadata: Dict, 
                       publish_time: str) -> Optional[str]:
        """
        Schedule a video for upload at a specific time
        """
        
        if not self.youtube:
            return None
        
        try:
            body = {
                "snippet": {
                    "title": metadata.get("title", "New Video"),
                    "description": metadata.get("description", ""),
                    "tags": metadata.get("tags", []),
                    "categoryId": "28"
                },
                "status": {
                    "privacyStatus": "private",
                    "publishAt": publish_time
                }
            }
            
            media = self.MediaFileUpload(
                video_file,
                chunksize=-1,
                resumable=True,
                mimetype='video/mp4'
            )
            
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            response = request.execute()
            video_id = response['id']
            
            print(f"✅ Video scheduled for: {publish_time}")
            print(f"Video ID: {video_id}")
            
            return video_id
        
        except Exception as e:
            print(f"Error scheduling video: {e}")
            return None
