# DocuGen-Ai
"AI-powered documentary video generation platform with OpenAI and ElevenLabs integration"

## Setup Instructions

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd docugen-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Configure the API URL in `.env`:
   ```
   VITE_API_URL=https://your-backend-api-url.com
   ```
   **Important**: Do not include credentials in the URL (e.g., `https://user:password@domain.com`). This will cause browser security errors.

5. Start the development server:
   ```bash
   npm run dev
   ```

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd docugen-backend
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Configure your API keys in `.env`:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ELEVENLABS_API_KEY`: Your ElevenLabs API key
   - `PEXELS_API_KEY`: Your Pexels API key
   - Other social media API keys as needed

5. Start the backend server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

## Production Deployment

### Frontend Production Configuration
For production deployment, configure the following environment variables:

1. **VITE_API_URL**: Set this to your actual backend API URL
   ```
   VITE_API_URL=https://your-backend-api-domain.com
   ```

2. Build the frontend for production:
   ```bash
   cd docugen-frontend
   npm run build
   ```

### Backend Production Configuration
For production deployment, configure the following environment variables:

1. **CORS_ORIGINS**: Set this to your frontend domain(s) for security
   ```
   CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
   ```
   
   For development, you can use `CORS_ORIGINS=*` to allow all origins.

2. **API Keys**: Configure all required API keys as shown in the backend setup section above.

### Important Notes
- **Development**: The Vite proxy automatically forwards `/api` requests to `http://localhost:8000` (or `VITE_PROXY_TARGET` if set)
- **Production**: The frontend will use `VITE_API_URL` to make direct API calls to your backend
- **Security**: Always set `CORS_ORIGINS` to specific domains in production, never use `*` in production environments
