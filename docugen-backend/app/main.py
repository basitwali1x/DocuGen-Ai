import app.pil_compat  # Apply PIL compatibility fix before any other imports

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import asyncio
from openai import OpenAI
from elevenlabs.client import ElevenLabs
import json
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.services.video_generator import VideoGenerator
from app.services.social_media import SocialMediaUploader

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DocuGen AI", description="AI-powered documentary video generation platform")

allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
video_generator = VideoGenerator()
social_uploader = SocialMediaUploader()

video_generations = []

class VideoGenerationRequest(BaseModel):
    topic: str
    niche: str
    aspect_ratios: Optional[List[str]] = ["16:9", "9:16", "1:1"]
    social_platforms: Optional[List[str]] = []

class VideoGenerationResponse(BaseModel):
    id: str
    topic: str
    niche: str
    status: str
    created_at: str
    aspect_ratios: Optional[List[str]] = None
    social_platforms: Optional[List[str]] = None

class SocialUploadRequest(BaseModel):
    generation_id: str
    platforms: List[str]

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/api/generations")
async def get_generations():
    return {"generations": video_generations}

@app.get("/api/download/{generation_id}")
async def download_audio(generation_id: str):
    generation = next((g for g in video_generations if g["id"] == generation_id), None)
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    if generation["status"] != "completed":
        raise HTTPException(status_code=400, detail="Generation not completed yet")
    
    audio_filename = f"voiceover_{generation_id}.mp3"
    file_path = f"/tmp/{audio_filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        path=file_path,
        filename=audio_filename,
        media_type="audio/mpeg"
    )

@app.get("/api/download-video/{generation_id}/{format}")
async def download_video(generation_id: str, format: str):
    generation = next((g for g in video_generations if g["id"] == generation_id), None)
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    if generation["status"] != "completed":
        raise HTTPException(status_code=400, detail="Generation not completed yet")
    
    video_files = generation.get("video_files", {})
    format_key = format.replace("x", ":")
    
    if format_key not in video_files or not video_files[format_key]:
        raise HTTPException(status_code=404, detail=f"Video file not found for format {format}")
    
    file_path = video_files[format_key]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found on disk")
    
    video_filename = f"documentary_{generation_id}_{format}.mp4"
    
    return FileResponse(
        path=file_path,
        filename=video_filename,
        media_type="video/mp4"
    )

@app.post("/api/generate-video")
async def generate_video(request: VideoGenerationRequest, x_api_key: str = Header(None, alias="X-API-Key")):
    logger.info(f"Incoming video generation request for topic: {request.topic}")
    logger.debug(f"Request details: {request.dict()}")

    if not x_api_key or x_api_key != os.getenv("BACKEND_API_KEY"):
        logger.error("Missing or invalid X-API-Key header")
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        generation_id = str(uuid.uuid4())
        logger.info(f"Starting video generation with ID: {generation_id}")
        
        generation = {
            "id": generation_id,
            "topic": request.topic,
            "niche": request.niche,
            "status": "generating",
            "created_at": datetime.now().isoformat(),
            "aspect_ratios": request.aspect_ratios,
            "social_platforms": request.social_platforms
        }
        video_generations.insert(0, generation)
        
        asyncio.create_task(process_video_generation(
            generation_id, 
            request.topic, 
            request.niche,
            request.aspect_ratios,
            request.social_platforms
        ))
        
        return VideoGenerationResponse(**generation)
        
    except Exception as e:
        logger.error(f"Critical error in video generation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-to-social")
async def upload_to_social(request: SocialUploadRequest):
    try:
        generation = next((g for g in video_generations if g["id"] == request.generation_id), None)
        if not generation:
            raise HTTPException(status_code=404, detail="Generation not found")
        
        if generation["status"] != "completed":
            raise HTTPException(status_code=400, detail="Generation not completed yet")
        
        video_files = generation.get("video_files", {})
        if not video_files:
            raise HTTPException(status_code=400, detail="No video files available")
        
        title = f"Documentary: {generation['topic']}"
        description = generation.get("description", f"An AI-generated documentary about {generation['topic']}")
        
        upload_results = social_uploader.upload_to_platforms(
            video_files, title, description, request.platforms
        )
        
        if "social_uploads" not in generation:
            generation["social_uploads"] = {}
        
        generation["social_uploads"].update(upload_results)
        
        return {"status": "success", "results": upload_results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to social media: {str(e)}")

async def process_video_generation(generation_id: str, topic: str, niche: str, 
                                   aspect_ratios: Optional[List[str]] = None, 
                                   social_platforms: Optional[List[str]] = None):
    try:
        generation = next((g for g in video_generations if g["id"] == generation_id), None)
        if not generation:
            return
            
        script_prompt = f"""Create a compelling documentary script about {topic} in the {niche} niche. 
        The script should be engaging, informative, and suitable for a 2-3 minute video.
        Include a strong opening hook, key facts, and a memorable conclusion.
        Format as a narrative script without stage directions."""
        
        try:
            script_response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional documentary scriptwriter."},
                    {"role": "user", "content": script_prompt}
                ],
                max_tokens=1000
            )
        except Exception as openai_error:
            logger.error(f"OpenAI API error for generation {generation_id}: {str(openai_error)}")
            raise Exception(f"Script generation failed: {str(openai_error)}")
        
        script = script_response.choices[0].message.content
        
        try:
            audio = elevenlabs_client.text_to_speech.convert(
                text=script,
                voice_id="JBFqnCBsd6RMkjVDRZzb",  # Default voice
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
        except Exception as elevenlabs_error:
            logger.error(f"ElevenLabs API error for generation {generation_id}: {str(elevenlabs_error)}")
            raise Exception(f"Voice generation failed: {str(elevenlabs_error)}")
        
        audio_filename = f"voiceover_{generation_id}.mp3"
        with open(f"/tmp/{audio_filename}", "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        description_prompt = f"""Create a brief, engaging description for a documentary video about {topic}. 
        Keep it under 200 characters and make it compelling for viewers."""
        
        try:
            description_response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a video marketing expert."},
                    {"role": "user", "content": description_prompt}
                ],
                max_tokens=100
            )
        except Exception as openai_error:
            logger.error(f"OpenAI API error for description generation {generation_id}: {str(openai_error)}")
            raise Exception(f"Description generation failed: {str(openai_error)}")
        
        description = description_response.choices[0].message.content
        
        video_files = {}
        if aspect_ratios:
            try:
                video_files = video_generator.generate_multiple_formats(
                    f"/tmp/{audio_filename}", script, topic, generation_id, aspect_ratios
                )
            except Exception as e:
                logger.error(f"Video generation failed for {generation_id}: {e}")
                video_files = {}
        
        generation["status"] = "completed"
        generation["script"] = script
        generation["description"] = description
        generation["audio_file"] = audio_filename
        generation["video_files"] = video_files
        generation["completed_at"] = datetime.now().isoformat()
        
        if social_platforms and video_files:
            try:
                title = f"Documentary: {topic}"
                upload_results = social_uploader.upload_to_platforms(
                    video_files, title, description, social_platforms
                )
                generation["social_uploads"] = upload_results
            except Exception as e:
                logger.error(f"Social media upload failed for {generation_id}: {e}")
                generation["social_uploads"] = {}
        
    except Exception as e:
        logger.error(f"Video generation failed for {generation_id}: {str(e)}")
        generation = next((g for g in video_generations if g["id"] == generation_id), None)
        if generation:
            generation["status"] = "failed"
            generation["failed_at"] = datetime.now().isoformat()
            
            error_message = str(e)
            
            if "Script generation failed:" in error_message:
                generation["error"] = "Failed to generate script using OpenAI. Please check your OpenAI API key and try again."
                generation["error_type"] = "openai_api"
            elif "Voice generation failed:" in error_message:
                generation["error"] = "Failed to generate voice using ElevenLabs. Please check your ElevenLabs API key and try again."
                generation["error_type"] = "elevenlabs_api"
            elif "Description generation failed:" in error_message:
                generation["error"] = "Failed to generate description using OpenAI. Please check your OpenAI API key and try again."
                generation["error_type"] = "openai_api"
            elif "MoviePy" in error_message or "video" in error_message.lower():
                generation["error"] = "Video processing failed. This may be due to system resources or video generation issues."
                generation["error_type"] = "video_processing"
            elif "Pexels" in error_message or "image" in error_message.lower():
                generation["error"] = "Image retrieval failed. Please check your Pexels API key and try again."
                generation["error_type"] = "image_service"
            else:
                generation["error"] = f"An unexpected error occurred: {error_message}"
                generation["error_type"] = "general"
