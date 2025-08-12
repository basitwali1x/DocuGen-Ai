"""PIL compatibility module to fix ANTIALIAS deprecation issues with MoviePy"""

try:
    from PIL import Image
    
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.Resampling.LANCZOS
        print("Applied PIL ANTIALIAS compatibility fix")
    
    PIL_AVAILABLE = True
except ImportError as e:
    print(f"PIL/Pillow not available: {e}")
    print("Video generation will be disabled, but audio generation will still work")
    PIL_AVAILABLE = False
