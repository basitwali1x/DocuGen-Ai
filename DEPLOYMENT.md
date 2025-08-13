# Deployment Requirements

## System Dependencies

The following system packages are required for video generation functionality:

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    ffmpeg
```

### Why These Dependencies Are Needed
- **libjpeg-dev, libpng-dev, etc.**: Required for PIL/Pillow image processing
- **ffmpeg**: Required for MoviePy video processing
- These dependencies allow PIL and MoviePy to compile and function properly

## Python Dependencies
Python dependencies are managed via Poetry and defined in `pyproject.toml`.

## Docker Deployment
If using Docker, add the following to your Dockerfile before installing Python dependencies:

```dockerfile
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

## Troubleshooting

### PIL/Pillow Import Errors
If you encounter errors like "No module named 'PIL'" or compilation errors:
1. Ensure system dependencies are installed
2. Reinstall pillow: `poetry install --no-cache`

### MoviePy Import Errors
If MoviePy fails to import or video processing fails:
1. Ensure ffmpeg is installed
2. Check that MoviePy can find ffmpeg: `poetry run python -c "import moviepy.config; print(moviepy.config.FFMPEG_BINARY)"`

### Video Generation Still Only Produces Audio
This indicates that the mock classes are still being used instead of the real libraries. Verify:
1. System dependencies are installed
2. Poetry environment is properly set up
3. No import errors in the application logs
