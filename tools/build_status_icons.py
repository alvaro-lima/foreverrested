"""Build original geometric status badges; no generated art or font glyphs."""
from pathlib import Path
from PIL import Image, ImageDraw

media = Path(__file__).resolve().parents[1] / 'Media'
scale = 16
edge = 32 * scale

def point(x, y):
    return (round(x * scale), round(y * scale))

colors = {
    'Current': (18, 91, 161), 'Next': (111, 37, 159),
    'NotStarted': (75, 75, 72), 'Done': (25, 118, 59),
    'InProgress': (167, 112, 13), 'Skipped': (162, 72, 22),
    'Failed': (152, 34, 36),
}
previews = []
fill = Image.new('RGBA',(edge,edge))
fill_draw = ImageDraw.Draw(fill)
fill_draw.ellipse((*point(3,3),*point(29,29)),fill=(255,255,255,185))
fill.resize((128,128),Image.Resampling.LANCZOS).save(media / 'StatusColorFill.tga',compression=None)
for name, color in colors.items():
    image = Image.new('RGBA', (edge, edge))
    draw = ImageDraw.Draw(image)
    draw.ellipse((*point(1, 1), *point(31, 31)), fill=(65, 43, 13, 255))
    draw.ellipse((*point(1.5, 1.5), *point(30.5, 30.5)), fill=(221, 179, 76, 255))
    # One uniform circular silhouette and a restrained vertical interior gradient.
    pixels = image.load()
    for y in range(edge):
        for x in range(edge):
            if (x / scale - 16) ** 2 + (y / scale - 16) ** 2 <= 13.2 ** 2:
                factor = 1.15 - .4 * y / edge
                pixels[x, y] = (*[min(255, round(c * factor)) for c in color], 255)
    glyph = Image.new('RGBA', (edge, edge))
    draw = ImageDraw.Draw(glyph)
    ink = (255, 235, 171, 255)
    def line(coords, width=2):
        draw.line([point(*p) for p in coords], fill=ink, width=round(width * scale), joint='curve')
    def polygon(coords):
        draw.polygon([point(*p) for p in coords], fill=ink)
    if name == 'Current':
        draw.ellipse((*point(9, 9), *point(23, 23)), outline=ink, width=round(2 * scale))
        draw.ellipse((*point(13.5, 13.5), *point(18.5, 18.5)), fill=ink)
    elif name == 'Next':
        polygon([(12, 8.5), (24, 16), (12, 23.5)])
    elif name == 'Done':
        line([(8, 16), (13.5, 21.5), (24, 10.5)], 3)
    elif name == 'InProgress':
        polygon([(10, 9), (22, 9), (22, 11), (17, 16), (22, 21), (22, 23),
                 (10, 23), (10, 21), (15, 16), (10, 11)])
    elif name == 'Skipped':
        polygon([(8, 9.5), (16, 16), (8, 22.5)])
        polygon([(17, 9.5), (25, 16), (17, 22.5)])
    elif name == 'Failed':
        line([(10, 10), (22, 22)], 3)
        line([(22, 10), (10, 22)], 3)
    glyph.resize((128,128),Image.Resampling.LANCZOS).save(media / f'StatusGlyph{name}.tga',compression=None)
    image.alpha_composite(glyph)
    final = image.resize((128, 128), Image.Resampling.LANCZOS)
    final.save(media / f'StatusVector{name}.tga', compression=None)
    assert final.getpixel((0, 0))[3] == 0
    previews.append(image.resize((28, 28), Image.Resampling.LANCZOS))
preview = Image.new('RGBA', (7 * 40, 40), (35, 32, 26, 255))
for index, icon in enumerate(previews):
    preview.alpha_composite(icon, (index * 40 + 6, 6))
preview.save(media / 'StatusVector-preview.png')
print('Built seven geometric status textures and a preview at 28 pixels.')
