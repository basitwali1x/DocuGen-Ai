# API Key Setup Instructions

## Issue Resolution: 401 "Invalid API key" Error

This document explains how to resolve the 401 "Invalid API key" authentication error when generating documentaries.

## Root Cause
The application requires matching API keys between the frontend and backend for authentication, but the required `.env` files were missing.

## Solution

### 1. Backend Configuration
Create `/docugen-backend/.env` file with the following content:

```env
# OpenAI API key (required for documentary generation)
OPENAI_API_KEY=your_openai_api_key_here

# ElevenLabs API key (for voice generation)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Pexels API key (for stock footage)
PEXELS_API_KEY=your_pexels_api_key_here

# Other API keys (optional)
YOUTUBE_API_KEY=your_youtube_api_key_here
FACEBOOK_ACCESS_TOKEN=your_facebook_token_here
TIKTOK_ACCESS_TOKEN=your_tiktok_token_here
INSTAGRAM_ACCESS_TOKEN=your_instagram_token_here

# Backend API key for authentication (must match frontend)
BACKEND_API_KEY=docugen-secret-key-2024

# CORS configuration
CORS_ORIGINS=*
```

### 2. Frontend Configuration
Create `/docugen-frontend/.env` file with the following content:

```env
# API URL for the DocuGen backend
VITE_API_URL=http://localhost:8000

# API key for backend authentication (must match backend)
VITE_API_KEY=docugen-secret-key-2024

# Proxy target for development
VITE_PROXY_TARGET=http://localhost:8000
```

### 3. Key Requirements
- The `BACKEND_API_KEY` in the backend .env must match `VITE_API_KEY` in the frontend .env
- For production, use secure random keys instead of the example key
- The OpenAI API key is required for documentary script generation
- ElevenLabs and Pexels API keys are optional but recommended for full functionality

## Testing
After creating both .env files:
1. Start backend: `cd docugen-backend && poetry run uvicorn app.main:app --reload`
2. Start frontend: `cd docugen-frontend && npm run dev`
3. Navigate to http://localhost:5173
4. Test documentary generation (e.g., "Malaysian Flight 370 Mystery" with "Mystery & Unexplained" niche)

## Security Notes
- Never commit .env files to version control
- Use environment-specific API keys
- Rotate keys regularly in production
- Use secure random strings for BACKEND_API_KEY in production
