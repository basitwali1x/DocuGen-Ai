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
