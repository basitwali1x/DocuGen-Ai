"""PIL compatibility module to fix ANTIALIAS deprecation issues with MoviePy"""

try:
    from PIL import Image
    
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.Resampling.LANCZOS
        print("Applied PIL ANTIALIAS compatibility fix")
except ImportError:
    print("PIL/Pillow not available - video generation will be disabled")
    pass
