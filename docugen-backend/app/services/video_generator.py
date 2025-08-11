import os
import requests

from PIL import Image, ImageDraw, ImageFont

if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS
    print("Applied PIL ANTIALIAS compatibility fix in video_generator")

try:
    from moviepy.editor import *
    MOVIEPY_AVAILABLE = True
except ImportError as e:
    print(f"MoviePy not available: {e}")
    MOVIEPY_AVAILABLE = False
    class AudioFileClip:
        def __init__(self, *args, **kwargs):
            pass
    class ImageClip:
        def __init__(self, *args, **kwargs):
            pass
    class CompositeVideoClip:
        def __init__(self, *args, **kwargs):
            pass
import tempfile
import logging
from typing import List, Dict, Optional, Tuple
import re

logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self):
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.temp_dir = "/tmp"
        
    def extract_keywords(self, script: str, topic: str) -> List[str]:
        keywords = [topic]
        
        script_words = re.findall(r'\b[A-Z][a-z]+\b', script)
        keywords.extend(script_words[:5])
        
        common_words = ['business', 'technology', 'nature', 'people', 'city', 'office']
        keywords.extend(common_words[:3])
        
        return list(set(keywords))[:8]
    
    def fetch_stock_footage(self, keywords: List[str], count: int = 10) -> List[Dict]:
        if not self.pexels_api_key:
            logger.warning("Pexels API key not found, using placeholder images")
            return self._get_placeholder_images(count)
        
        headers = {"Authorization": self.pexels_api_key}
        images = []
        
        for keyword in keywords[:3]:
            try:
                url = f"https://api.pexels.com/v1/search"
                params = {
                    "query": keyword,
                    "per_page": min(count // len(keywords[:3]) + 1, 15),
                    "orientation": "landscape"
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for photo in data.get("photos", []):
                        images.append({
                            "url": photo["src"]["large"],
                            "keyword": keyword,
                            "id": photo["id"]
                        })
                        if len(images) >= count:
                            break
                            
            except Exception as e:
                logger.error(f"Error fetching images for keyword '{keyword}': {e}")
                continue
                
            if len(images) >= count:
                break
        
        if not images:
            return self._get_placeholder_images(count)
            
        return images[:count]
    
    def _get_placeholder_images(self, count: int) -> List[Dict]:
        placeholder_images = []
        colors = [(52, 152, 219), (155, 89, 182), (46, 204, 113), (241, 196, 15), (231, 76, 60)]
        
        for i in range(count):
            color = colors[i % len(colors)]
            placeholder_images.append({
                "url": f"placeholder_{i}",
                "keyword": "placeholder",
                "id": f"placeholder_{i}",
                "color": color
            })
        
        return placeholder_images
    
    def download_image(self, image_data: Dict) -> Optional[str]:
        try:
            if image_data["url"].startswith("placeholder_"):
                return self._create_placeholder_image(image_data)
            
            response = requests.get(image_data["url"], timeout=15)
            if response.status_code == 200:
                filename = f"{self.temp_dir}/image_{image_data['id']}.jpg"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return filename
        except Exception as e:
            logger.error(f"Error downloading image {image_data['id']}: {e}")
            return self._create_placeholder_image(image_data)
        
        return None
    
    def _create_placeholder_image(self, image_data: Dict) -> str:
        width, height = 1920, 1080
        color = image_data.get("color", (100, 100, 100))
        
        img = Image.new('RGB', (width, height), color)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        text = image_data.get("keyword", "Documentary").title()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        filename = f"{self.temp_dir}/placeholder_{image_data['id']}.jpg"
        img.save(filename, 'JPEG')
        return filename
    
    def create_video(self, audio_file: str, script: str, topic: str, generation_id: str, 
                    aspect_ratio: str = "16:9") -> Optional[str]:
        if not MOVIEPY_AVAILABLE:
            logger.error("MoviePy not available - video creation disabled")
            return None
            
        try:
            keywords = self.extract_keywords(script, topic)
            images_data = self.fetch_stock_footage(keywords, count=8)
            
            image_files = []
            for img_data in images_data:
                img_file = self.download_image(img_data)
                if img_file:
                    image_files.append(img_file)
            
            if not image_files:
                logger.error("No images available for video creation")
                return None
            
            audio_clip = AudioFileClip(audio_file)
            duration = audio_clip.duration
            
            dimensions = self._get_dimensions(aspect_ratio)
            if not dimensions:
                logger.error(f"Invalid aspect ratio: {aspect_ratio}")
                return None
            
            width, height = dimensions
            
            clips = []
            image_duration = duration / len(image_files)
            
            for i, img_file in enumerate(image_files):
                try:
                    processed_img_file = self._preprocess_image_for_moviepy(img_file, width, height)
                    if not processed_img_file:
                        logger.error(f"Failed to preprocess image {img_file}")
                        continue
                    
                    img_clip = ImageClip(processed_img_file, duration=image_duration)
                    
                    if i > 0:
                        img_clip = img_clip.crossfadein(0.5)
                    if i < len(image_files) - 1:
                        img_clip = img_clip.crossfadeout(0.5)
                    
                    img_clip = img_clip.set_start(i * image_duration)
                    clips.append(img_clip)
                    
                except Exception as e:
                    logger.error(f"Error processing image {img_file}: {e}")
                    continue
            
            if not clips:
                logger.error("No valid image clips created")
                return None
            
            video = CompositeVideoClip(clips, size=(width, height))
            video = video.set_audio(audio_clip)
            video = video.set_duration(duration)
            
            output_filename = f"{self.temp_dir}/video_{generation_id}_{aspect_ratio.replace(':', 'x')}.mp4"
            
            video.write_videofile(
                output_filename,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=f"{self.temp_dir}/temp_audio_{generation_id}.m4a",
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            video.close()
            audio_clip.close()
            for clip in clips:
                clip.close()
            
            for img_file in image_files:
                try:
                    if os.path.exists(img_file):
                        os.remove(img_file)
                except:
                    pass
            
            return output_filename
            
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return None
    
    def _get_dimensions(self, aspect_ratio: str) -> Optional[Tuple[int, int]]:
        dimensions_map = {
            "16:9": (1920, 1080),
            "9:16": (1080, 1920),
            "1:1": (1080, 1080)
        }
        return dimensions_map.get(aspect_ratio)
    
    def _preprocess_image_for_moviepy(self, img_file: str, target_width: int, target_height: int) -> Optional[str]:
        """Preprocess image to avoid PIL compatibility issues with MoviePy"""
        try:
            with Image.open(img_file) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize image to target dimensions
                img_resized = img.resize((target_width, target_height), Image.ANTIALIAS)
                
                processed_filename = f"{self.temp_dir}/processed_{os.path.basename(img_file)}"
                img_resized.save(processed_filename, 'JPEG', quality=95)
                
                return processed_filename
                
        except Exception as e:
            logger.error(f"Error preprocessing image {img_file}: {e}")
            return None
    
    def generate_multiple_formats(self, audio_file: str, script: str, topic: str, 
                                 generation_id: str, formats: List[str] = None) -> Dict[str, Optional[str]]:
        if formats is None:
            formats = ["16:9", "9:16", "1:1"]
        
        results = {}
        for format_ratio in formats:
            try:
                video_file = self.create_video(audio_file, script, topic, generation_id, format_ratio)
                results[format_ratio] = video_file
                logger.info(f"Created video for {format_ratio}: {video_file}")
            except Exception as e:
                logger.error(f"Failed to create video for {format_ratio}: {e}")
                results[format_ratio] = None
        
        return results
