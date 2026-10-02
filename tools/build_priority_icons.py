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
        steel, edge, light = '#ecbb31', '#381f09', '#ffe28b'
        # A headless suit of armor: shoulder plates, chest, arms and greaves.
        pieces = [
            [(111,10),(145,10),(151,25),(175,32),(186,43),(176,65),(163,57),(158,131),(128,145),(98,131),(93,57),(80,65),(70,43),(81,32),(105,25)],
            [(71,42),(91,57),(77,95),(69,145),(52,145),(49,120),(57,70)],
            [(185,42),(165,57),(179,95),(187,145),(204,145),(207,120),(199,70)],
            [(98,134),(128,149),(158,134),(162,153),(128,165),(94,153)],
            [(94,156),(125,167),(121,195),(110,217),(86,208),(83,180)],
            [(162,156),(131,167),(135,195),(146,217),(170,208),(173,180)],
            [(86,205),(110,213),(107,244),(83,244),(78,224)],
            [(170,205),(146,213),(149,244),(173,244),(178,224)],
        ]
        for points in pieces:
            d.polygon(points, fill=steel, outline=edge, width=4)
        d.rounded_rectangle((105,43,151,111), radius=12, fill=(0,0,0,0))
        d.line((101,126,128,139,155,126), fill=light, width=4)
        d.polygon([(87,221),(101,211),(99,237),(88,237)], fill=(0,0,0,0))
        d.polygon([(169,221),(155,211),(157,237),(168,237)], fill=(0,0,0,0))
    elif name == 'Money':
        # Silver behind, gold and copper in front. Broad shading survives
        # the small inline size better than lettering or tiny milled edges.
        stacks = [
            (91,18,100,8,'#d9e0e7','#98a2ad','#59636f','#f4f6f8'),
            (10,130,112,4,'#ecbb31','#b78317','#73500d','#ffe28b'),
            (140,145,106,4,'#cf853e','#a25c26','#653a1b','#efb57b'),
        ]
        for x,y,w,count,face,side,edge,highlight in stacks:
            for layer in range(count-1,-1,-1):
                top = y + layer * 15
                d.ellipse((x,top+12,x+w,top+42), fill=side, outline=edge, width=3)
                d.rectangle((x,top+15,x+w,top+27), fill=side)
                d.line((x,top+16,x,top+27), fill=edge, width=3)
                d.line((x+w,top+16,x+w,top+27), fill=edge, width=3)
                d.ellipse((x,top,x+w,top+30), fill=face, outline=edge, width=3)
                d.arc((x+7,top+4,x+w-7,top+26), 185, 350, fill=highlight, width=3)
            d.ellipse((x+14,y+6,x+w-14,y+24), outline=highlight, width=3)
    else:
        d.line([(128,24),(232,128),(128,232),(24,128),(128,24)], fill='#65baff', width=22, joint='curve')
    if name in ('Money', 'Gear'):
        im.save(media / ('Priority'+name+'-source.png'))
    # Prefilter the small markers near their ~20px display size to avoid
    # aliasing its diagonal edges when WoW downsizes a large texture.
    texture_size = 32
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
