"""Authored head views and explicit pose attachments, baked before runtime."""
import hashlib,json,math
from functools import lru_cache
from pathlib import Path
from PIL import Image,ImageOps

HERE=Path(__file__).resolve().parents[1]
CATALOG=HERE/'assets/character-identities.json'

@lru_cache(maxsize=8)
def _json(path,mtime):return json.loads(Path(path).read_text(encoding='utf8'))

def catalog():
    return _json(str(CATALOG),CATALOG.stat().st_mtime_ns) if CATALOG.exists() else {'bodies':{}}

def sources(student):
    identity=student.get('identity','default')
    if identity=='default':return []
    c=catalog();entry=c['bodies'][student['body']][identity]
    return [Path(__file__),CATALOG,HERE/c['attachments'][student['body']],
            *(HERE/p for p in entry['views'].values())]

def fingerprint(student):
    digest=hashlib.sha256()
    for p in sources(student):digest.update(p.read_bytes())
    return digest.hexdigest()

def attachments(body,group='base'):
    c=catalog()
    path=HERE/c['attachments'][body]
    return _json(str(path),path.stat().st_mtime_ns)[group]

@lru_cache(maxsize=128)
def _view(path,mtime,scale):
    with Image.open(path) as source:im=source.convert('RGBA')
    return im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)

def head(student,attachment):
    entry=catalog()['bodies'][student['body']][student['identity']]
    path=HERE/entry['views'][attachment['view']]
    # Constant authored scale across every pose; inclinations have explicit anchors.
    scale=entry['scale'];im=_view(str(path),path.stat().st_mtime_ns,scale)
    if attachment.get('mirror'):im=ImageOps.mirror(im)
    angle=attachment.get('angle',0)
    original_size=im.size
    if angle:im=im.rotate(angle,Image.Resampling.NEAREST,expand=True)
    x,y=attachment['anchor'];pivot=entry['pivots'][attachment['view']]
    # Rotate the attachment mathematically; a one-pixel marker can disappear
    # when nearest-neighbor rotation samples between pixels.
    w,h=original_size;px=min(w-1,round(pivot[0]*scale));py=min(h-1,round(pivot[1]*scale))
    if attachment.get('mirror'):px=w-1-px
    if angle:
        a=math.radians(angle);dx=px+.5-w/2;dy=py+.5-h/2
        px=round(math.cos(a)*dx+math.sin(a)*dy+im.width/2-.5)
        py=round(-math.sin(a)*dx+math.cos(a)*dy+im.height/2-.5)
    left,top=x-px,y-py
    if 'floor' in attachment:top=min(top,attachment['floor']+1-im.height)
    if left<0 or top<0 or left+im.width>224 or top+im.height>144:
        raise ValueError('Identity head clips pose: '+str(attachment))
    result=Image.new('RGBA',(224,144));result.paste(im,(left,top));return result

def replace(frame,student,attachment,foreground=None):
    from compile_character import skin
    result=frame.copy();mask=Image.new('L',result.size)
    # Explicit polygon removes only the original head's skin and hair.
    from PIL import ImageDraw
    ImageDraw.Draw(mask).polygon([tuple(p) for p in attachment['remove']],fill=255)
    region=mask.getbbox() or (0,0,0,0)
    # The gi is open at the neck. Head masks must not punch holes in the chest
    # or erase crossing forearms below the attachment. Floor poses use their
    # separately authored horizontal removal polygons instead.
    skin_cutoff=attachment.get('skin_cutoff',attachment['anchor'][1]-6 if abs(attachment.get('angle',0))<45 and 'floor' not in attachment else None)
    preserved=Image.new('RGBA',result.size)
    for y in range(region[1],region[3]):
        for x in range(region[0],region[2]):
            r,g,b,a=frame.getpixel((x,y))
            if mask.getpixel((x,y)) and a and min(r,g,b)>125 and max(r,g,b)-min(r,g,b)<65:preserved.putpixel((x,y),(r,g,b,a))
    for rect in attachment.get('occlusion',[]):
        crop=result.crop(rect);preserved.paste(crop,rect[:2])
    for y in range(region[1],region[3]):
        for x in range(region[0],region[2]):
            r,g,b,a=result.getpixel((x,y))
            if skin_cutoff is not None and y>=skin_cutoff and skin((r,g,b)):continue
            if mask.getpixel((x,y)) and a and (skin((r,g,b)) or max(r,g,b)<125):
                result.putpixel((x,y),(0,0,0,0))
    new_head=head(student,attachment)
    result.alpha_composite(new_head)
    # Original white gi and crossing limbs stay in front of the head.
    if foreground is not None:result.alpha_composite(foreground)
    result.alpha_composite(preserved)
    return result,new_head.getbbox()

def paint(frame,student,new_head):
    from compile_character import skin,shade
    from character_registry import SKINS,HAIR_COLORS
    from skin_palette import apply_skin_palette
    appearance=student['appearance'];result=apply_skin_palette(frame,appearance['skin'])
    target_skin=SKINS[appearance['skin']];target_hair=HAIR_COLORS[appearance['hair_color']]
    if target_skin is None and target_hair is None:return result
    entry=catalog()['bodies'][student['body']][student['identity']]
    if entry.get('bald'):target_hair=None
    hair_mask=Image.new('L',frame.size)
    if target_hair:
        from PIL import ImageFilter
        from character_masks import components
        for y in range(144):
            for x in range(224):
                r,g,b,a=new_head.getpixel((x,y))
                if a and max(r,g,b)<110 and not skin((r,g,b)):hair_mask.putpixel((x,y),255)
        groups=components(hair_mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)))
        hair_mask=Image.new('L',frame.size)
        if groups:
            for i in groups[0]:hair_mask.putpixel((i%224,i//224),255)
    for y in range(144):
        for x in range(224):
            r,g,b,a=result.getpixel((x,y))
            if not a:continue
            if target_hair and hair_mask.getpixel((x,y)) and new_head.getpixel((x,y))[3] and 23<max(r,g,b)<110 and not skin((r,g,b)):
                # Protect black contours; only internal hair shading is recolored.
                light=.35+.65*min(1,max(r,g,b)/110)
                result.putpixel((x,y),(*(min(255,round(c*light)) for c in target_hair),a))
    return result
