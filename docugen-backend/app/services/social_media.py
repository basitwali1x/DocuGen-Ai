import os
import logging
from typing import Dict, Optional, Any
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests

logger = logging.getLogger(__name__)

class SocialMediaUploader:
    def __init__(self):
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.facebook_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.tiktok_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        self.instagram_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    
    def upload_to_youtube(self, video_file: str, title: str, description: str, 
                         tags: list = None) -> Dict[str, Any]:
        try:
            if not self.youtube_api_key:
                return {"status": "error", "message": "YouTube API key not configured"}
            
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': '22'
                },
                'status': {
                    'privacyStatus': 'public'
                }
            }
            
            media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
            
            request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = request.execute()
            
            video_id = response.get('id')
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            return {
                "status": "success",
                "url": video_url,
                "video_id": video_id,
                "message": "Successfully uploaded to YouTube"
            }
            
        except Exception as e:
            logger.error(f"YouTube upload error: {e}")
            return {"status": "error", "message": f"YouTube upload failed: {str(e)}"}
    
    def upload_to_tiktok(self, video_file: str, title: str, description: str) -> Dict[str, Any]:
        try:
            if not self.tiktok_token:
                return {"status": "error", "message": "TikTok access token not configured"}
            
            return {"status": "pending", "message": "TikTok upload requires OAuth flow - feature coming soon"}
            
        except Exception as e:
            logger.error(f"TikTok upload error: {e}")
            return {"status": "error", "message": f"TikTok upload failed: {str(e)}"}
    
    def upload_to_facebook(self, video_file: str, title: str, description: str) -> Dict[str, Any]:
        try:
            if not self.facebook_token:
                return {"status": "error", "message": "Facebook access token not configured"}
            
            return {"status": "pending", "message": "Facebook upload requires page access - feature coming soon"}
            
        except Exception as e:
            logger.error(f"Facebook upload error: {e}")
            return {"status": "error", "message": f"Facebook upload failed: {str(e)}"}
    
    def upload_to_instagram(self, video_file: str, title: str, description: str) -> Dict[str, Any]:
        try:
            if not self.instagram_token:
                return {"status": "error", "message": "Instagram access token not configured"}
            
            return {"status": "pending", "message": "Instagram upload requires business account - feature coming soon"}
            
        except Exception as e:
            logger.error(f"Instagram upload error: {e}")
            return {"status": "error", "message": f"Instagram upload failed: {str(e)}"}
    
    def upload_to_platforms(self, video_files: Dict[str, str], title: str, 
                           description: str, platforms: list) -> Dict[str, Dict[str, Any]]:
        results = {}
        
        platform_format_map = {
            "youtube": "16:9",
            "tiktok": "9:16",
            "facebook": "16:9",
            "instagram": "1:1"
        }
        
        for platform in platforms:
            if platform not in platform_format_map:
                results[platform] = {"status": "error", "message": f"Unsupported platform: {platform}"}
                continue
            
            required_format = platform_format_map[platform]
            video_file = video_files.get(required_format)
            
            if not video_file or not os.path.exists(video_file):
                results[platform] = {
                    "status": "error", 
                    "message": f"Video file not found for format {required_format}"
                }
                continue
            
            if platform == "youtube":
                results[platform] = self.upload_to_youtube(video_file, title, description)
            elif platform == "tiktok":
                results[platform] = self.upload_to_tiktok(video_file, title, description)
            elif platform == "facebook":
                results[platform] = self.upload_to_facebook(video_file, title, description)
            elif platform == "instagram":
                results[platform] = self.upload_to_instagram(video_file, title, description)
        
        return results
