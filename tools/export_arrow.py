"""Package generated transparent artwork as a power-of-two WoW TGA texture."""
from pathlib import Path
import shutil
import sys
from PIL import Image

source = Path(sys.argv[1])
destination = Path(__file__).resolve().parents[1] / "Media"
destination.mkdir(exist_ok=True)
shutil.copy2(source, destination / "BronzeArrow-source.png")
image = Image.open(source).convert("RGBA")
bounds = image.getchannel("A").getbbox()
if bounds is None:
    raise ValueError("Arrow has no visible pixels")
sprite = image.crop(bounds)
edge = round(max(sprite.size) * 1.15)
canvas = Image.new("RGBA", (edge, edge), (0, 0, 0, 0))
canvas.paste(sprite, ((edge - sprite.width) // 2, (edge - sprite.height) // 2))
texture = canvas.resize((128, 128), Image.Resampling.LANCZOS)
texture.save(destination / "BronzeArrow.tga", compression=None)
check = Image.open(destination / "BronzeArrow.tga")
assert check.size == (128, 128) and check.mode == "RGBA"
assert check.getchannel("A").getextrema() == (0, 255)
print("Exported Media/BronzeArrow.tga: 128x128 RGBA, preserved transparency")
