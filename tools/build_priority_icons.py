"""Build small, transparent WoW TGA markers and a review preview (Pillow)."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
media = root / 'Media'
icons = {}
for name in ('Critical', 'Gear', 'Money'):
    im = Image.new('RGBA', (256, 256)); d = ImageDraw.Draw(im)
    if name == 'Critical':
        d.polygon([(10,16),(246,16),(128,242)], fill='#ecbb31', outline='#381f09', width=10)
        d.rounded_rectangle((112,50,144,129), radius=6, fill='#381f09')
        d.ellipse((112,149,144,175), fill='#381f09')
    elif name == 'Gear':
        d.line((67,209,171,86), fill='#18394e', width=39)
        d.line((67,209,171,86), fill='#65baff', width=25)
        d.polygon([(71,56),(109,15),(229,112),(192,158)], fill='#65baff', outline='#18394e', width=9)
        d.line((94,53,202,139), fill='#b4e4ff', width=7)
    elif name == 'Money':
        for x,y,color,edge in [(16,16,'#f5c542','#a87713'),(82,64,'#d9e0e7','#798590'),(130,116,'#ba783d','#70411e')]:
            d.ellipse((x,y,x+108,y+108), fill=color, outline=edge, width=7)
            d.ellipse((x+13,y+13,x+95,y+95), outline=edge, width=3)
    else:
        d.line([(128,24),(232,128),(128,232),(24,128),(128,24)], fill='#65baff', width=22, joint='curve')
    # Prefilter the critical marker near its ~20px display size to avoid
    # aliasing its diagonal edges when WoW downsizes a large texture.
    texture_size = 32 if name == 'Critical' else 64
    icon = im.resize((texture_size,texture_size), Image.Resampling.LANCZOS)
    icon.save(media / ('Priority'+name+'.tga'), compression=None)
    icons[name] = icon
preview = Image.new('RGBA', (320,112), '#211b26')
draw = ImageDraw.Draw(preview)
labels = {'Critical': 'Key quest', 'Gear': 'Quest with gear reward', 'Money': 'Quest with money reward'}
for i,(name,icon) in enumerate(icons.items()):
    label=labels[name]
    draw.text((12,i*36+12), label, fill='white')
    preview.alpha_composite(icon.resize((24,24),Image.Resampling.LANCZOS), (20+int(draw.textlength(label)),i*36+4))
preview.convert('RGB').save(media / 'PriorityIcons-preview.png')
