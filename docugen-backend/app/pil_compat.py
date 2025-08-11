"""PIL compatibility module to fix ANTIALIAS deprecation issues with MoviePy"""

from PIL import Image

if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS
    print("Applied PIL ANTIALIAS compatibility fix")
