from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import asyncio
from openai import OpenAI
from elevenlabs.client import ElevenLabs
import json
import uuid
from datetime import datetime

load_dotenv()

app = FastAPI(title="DocuGen AI", description="AI-powered documentary video generation platform")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

video_generations = []

class VideoGenerationRequest(BaseModel):
    topic: str
    niche: str

class VideoGenerationResponse(BaseModel):
    id: str
    topic: str
    niche: str
    status: str
    created_at: str

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/api/generations")
async def get_generations():
    return {"generations": video_generations}

@app.post("/api/generate-video")
async def generate_video(request: VideoGenerationRequest):
    try:
        generation_id = str(uuid.uuid4())
        generation = {
            "id": generation_id,
            "topic": request.topic,
            "niche": request.niche,
            "status": "generating",
            "created_at": datetime.now().isoformat()
        }
        video_generations.insert(0, generation)
        
        asyncio.create_task(process_video_generation(generation_id, request.topic, request.niche))
        
        return VideoGenerationResponse(**generation)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start video generation: {str(e)}")

async def process_video_generation(generation_id: str, topic: str, niche: str):
    try:
        generation = next((g for g in video_generations if g["id"] == generation_id), None)
        if not generation:
            return
            
        script_prompt = f"""Create a compelling documentary script about {topic} in the {niche} niche. 
        The script should be engaging, informative, and suitable for a 2-3 minute video.
        Include a strong opening hook, key facts, and a memorable conclusion.
        Format as a narrative script without stage directions."""
        
        script_response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional documentary scriptwriter."},
                {"role": "user", "content": script_prompt}
            ],
            max_tokens=1000
        )
        
        script = script_response.choices[0].message.content
        
        audio = elevenlabs_client.text_to_speech.convert(
            text=script,
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # Default voice
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        audio_filename = f"voiceover_{generation_id}.mp3"
        with open(f"/tmp/{audio_filename}", "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        description_prompt = f"""Create a brief, engaging description for a documentary video about {topic}. 
        Keep it under 200 characters and make it compelling for viewers."""
        
        description_response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a video marketing expert."},
                {"role": "user", "content": description_prompt}
            ],
            max_tokens=100
        )
        
        description = description_response.choices[0].message.content
        
        generation["status"] = "completed"
        generation["script"] = script
        generation["description"] = description
        generation["audio_file"] = audio_filename
        generation["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        generation = next((g for g in video_generations if g["id"] == generation_id), None)
        if generation:
            generation["status"] = "failed"
            generation["error"] = str(e)
            generation["failed_at"] = datetime.now().isoformat()
