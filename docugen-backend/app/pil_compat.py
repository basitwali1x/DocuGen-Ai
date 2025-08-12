"""PIL compatibility module to fix ANTIALIAS deprecation issues with MoviePy"""

from PIL import Image

try:
    Image.ANTIALIAS
except AttributeError:
    Image.ANTIALIAS = Image.Resampling.LANCZOS
    print("Applied PIL ANTIALIAS compatibility fix for newer Pillow versions")
