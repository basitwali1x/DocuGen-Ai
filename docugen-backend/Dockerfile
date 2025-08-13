FROM python:3.12-slim-bullseye

# Install system dependencies required for video generation
RUN apt-get update && apt-get install -y \
    libjpeg62-turbo \
    libjpeg62-turbo-dev \
    libgl1 \
    libmagic1 \
    ffmpeg \
    zlib1g-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Configure poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies without installing the current project
RUN poetry install --no-root

# Reinstall pillow with system dependencies available
RUN pip uninstall -y pillow
RUN pip install --no-cache-dir --force-reinstall pillow

# Copy application code
COPY . .

# Test dependencies during build
RUN python -c "from PIL import Image; print('PIL OK')" && \
    python -c "from moviepy.editor import AudioFileClip; print('MoviePy OK')" && \
    echo "All dependencies working"

# Add health check endpoint for deep verification
RUN echo "Dependencies verified during build"

# Expose port
EXPOSE 8000

# Set environment variables directly
ARG OPENAI_API_KEY
ARG ELEVENLABS_API_KEY  
ARG PEXELS_API_KEY
ARG BACKEND_API_KEY=deployment-test-key-123
ARG CORS_ORIGINS=*

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
ENV PEXELS_API_KEY=${PEXELS_API_KEY}
ENV BACKEND_API_KEY=${BACKEND_API_KEY}
ENV CORS_ORIGINS=${CORS_ORIGINS}

# Start the application
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
