"""Build small, transparent WoW TGA markers and a review preview (Pillow)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops

root = Path(__file__).resolve().parents[1]
media = root / 'Media'
icons = {}
for name in ('Critical', 'Optional', 'OptionalTurnin', 'OptionalObjective', 'OptionalTravel', 'Objective', 'Gear', 'Money', 'Catchup'):
    im = Image.new('RGBA', (256, 256)); d = ImageDraw.Draw(im)
    if name == 'OptionalTurnin':
        # Native-sized compact hook, traced in a 10-by-17 coordinate grid.
        # Keep its narrow silhouette and softened crown rather than expanding
        # a generic question mark to fill the whole inline texture.
        mask = Image.new('L', (256,256))
        md = ImageDraw.Draw(mask)
        points = [(3,0),(8,0),(9.5,1),(10,2.5),(9,6),
                  (6.5,8.5),(5.5,10),(5,12),(2,12),
                  (2,9.5),(3.5,7.5),(6,5),(6.5,3.5),
                  (3.5,3.5),(3,5),(0,5),(0,2.5),(1,1)]
        md.polygon([(64+x*12.8,19+y*12.8) for x,y in points], fill=255)
        md.ellipse((86,198,129,237), fill=255)
        outline = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(21)))
        im = Image.new('RGBA', (256,256), '#ecbb31')
        im.putalpha(outline)
    elif name == 'OptionalObjective':
        source = Image.open(media / 'PriorityObjective-source.png').convert('RGBA')
        source = source.crop(source.getbbox())
        source.thumbnail((208,208))
        im.alpha_composite(source, ((256-source.width)//2, (256-source.height)//2))
        mask = im.getchannel('A').point(lambda value: 255 if value > 100 else 0)
        outline = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(15)))
        im = Image.new('RGBA', (256,256), '#ecbb31')
        im.putalpha(outline)
    elif name == 'Catchup':
        source = Image.open(media / 'PriorityCatchup-source.png').convert('RGBA')
        source = source.crop(source.getbbox())
        im = Image.new('RGBA', (max(source.size)+48,)*2)
        im.alpha_composite(source, ((im.width-source.width)//2, (im.height-source.height)//2))
    elif name == 'Objective':
        im = Image.open(media / 'PriorityObjective-source.png').convert('RGBA')
    elif name == 'OptionalTravel':
        d.ellipse((24,24,232,232), outline='#ecbb31', width=18)
        d.ellipse((98,98,158,158), fill='#ecbb31')
    elif name == 'Optional':
        im = Image.open(media / 'PriorityOptional-source.png').convert('RGBA')
    elif name == 'Critical':
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
preview = Image.new('RGBA', (320,len(icons)*36), '#211b26')
draw = ImageDraw.Draw(preview)
labels = {'Critical': 'Key quest', 'Optional': 'Optional accept', 'OptionalTurnin': 'Optional turn-in', 'OptionalObjective': 'Optional objectives', 'OptionalTravel': 'Optional travel', 'Objective': 'Quest objectives', 'Gear': 'Quest with gear reward', 'Money': 'Quest with money reward', 'Catchup': 'Catch-up quest'}
for i,(name,icon) in enumerate(icons.items()):
    label=labels[name]
    draw.text((12,i*36+12), label, fill='white')
    preview.alpha_composite(icon.resize((24,24),Image.Resampling.LANCZOS), (20+int(draw.textlength(label)),i*36+4))
preview.convert('RGB').save(media / 'PriorityIcons-preview.png')
