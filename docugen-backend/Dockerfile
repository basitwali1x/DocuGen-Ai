FROM python:3.12

# Install system dependencies for Pillow, MoviePy and video processing
RUN apt-get update && apt-get install -y \
    libjpeg62-turbo-dev \
    libjpeg62-turbo \
    libpng-dev \
    libpng16-16 \
    libtiff5-dev \
    libtiff5 \
    libfreetype6-dev \
    libfreetype6 \
    liblcms2-dev \
    liblcms2-2 \
    libwebp-dev \
    libwebp7 \
    libharfbuzz-dev \
    libharfbuzz0b \
    libfribidi-dev \
    libfribidi0 \
    libxcb1-dev \
    libxcb1 \
    zlib1g-dev \
    zlib1g \
    pkg-config \
    gcc \
    g++ \
    build-essential \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libavresample-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
