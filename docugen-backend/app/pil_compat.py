"""PIL compatibility module to fix ANTIALIAS deprecation issues with MoviePy"""

def apply_pil_compatibility():
    """Apply PIL compatibility fix only when needed"""
    try:
        from PIL import Image
        
        if not hasattr(Image, 'ANTIALIAS'):
            Image.ANTIALIAS = Image.Resampling.LANCZOS
            print("Applied PIL ANTIALIAS compatibility fix")
        
        return True
    except ImportError as e:
        print(f"PIL/Pillow not available: {e}")
        print("Video generation will be disabled, but audio generation will still work")
        return False

PIL_AVAILABLE = None
