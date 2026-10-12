"""Notebook-only appearance preparation; Pillow, binary alpha, no combat changes.

Equivalent appearances share one content-addressed atlas regardless of name/belt.
Compact shelf packing avoids empty 224x144 cells. Runtime only blits old quads.
"""
import argparse,json,math,sys
from pathlib import Path
from PIL import Image,ImageOps,ImageFilter
from character_registry import read,write,validate,visual_key,SKINS,HAIR_COLORS,BUILDS
from skin_palette import apply_skin_palette
HERE=Path(__file__).resolve().parents[1]

def skin(rgb):
    r,g,b=rgb
    return r>55 and r>g*1.055 and g>b*1.015 and r-b>16 and (r-b)/max(r,1)>.08
def shade(rgb,target):
    # Preserve highlights/contours and the authored pixel grid.
    light=max(.23,min(1.18,max(rgb)/210))
    return tuple(min(255,round(c*light)) for c in target)
def layer_frames(body,layer,variant,manifest):
    part=manifest[body]['parts'][layer][variant]
    with Image.open(HERE/'src/assets'/(part['right']+'.png')) as source:
        frames=[]
        for f in part['frames']:
            im=Image.new('RGBA',(224,144));im.paste(source.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']));frames.append(im)
    return frames
def transform(frame,appearance,bounds=None):
    sx=BUILDS[appearance['build']];sy=appearance['height']
    if sx==1 and sy==1:return frame
    # Scale the same logical canvas for every layer, retaining exact pixel alignment.
    padding=frame.height-144
    if padding:
        width=round(224*sx);body=frame.crop((0,padding,224,frame.height)).resize((width,round(144*sy)),Image.Resampling.NEAREST)
        upper=frame.crop((0,0,224,padding)).resize((width,round(padding*sy)),Image.Resampling.NEAREST)
        crop=Image.new('RGBA',(width,upper.height+body.height));crop.paste(upper,(0,0));crop.paste(body,(0,upper.height))
        y=143+padding-round(143*sy)-upper.height
    else:
        crop=frame.resize((round(224*sx),round(144*sy)),Image.Resampling.NEAREST);y=143-round(143*sy)
    x=112-round(112*sx)
    # Wide archived poses can reach the cell edge. Shift every layer equally,
    # using the shared pose bounds, rather than clipping an extended hand/foot.
    bounds=bounds or frame.getbbox()
    if bounds:x=max(-math.floor(bounds[0]*sx),min(x,224-math.ceil(bounds[2]*sx)))
    b=crop.getbbox()
    if b and (x+b[0]<0 or y+b[1]<0 or x+b[2]>224 or y+b[3]>frame.height):raise ValueError('Esta proporcao recorta uma pose; use altura/porte menores.')
    im=Image.new('RGBA',(224,frame.height));im.paste(crop,(x,y));im.info.update(frame.info);return im
def pack(frames,name,out):
    crops=[]
    for frame in frames:
        b=frame.getbbox() or (0,0,1,1);crops.append((b,frame.crop(b)))
    layouts=[]
    for shelf_width in range(max(224,max(c.width for _,c in crops)),513,8):
        records=[];x=y=row=used=0
        for b,crop in crops:
            if x+crop.width>shelf_width:x=0;y+=row;row=0
            records.append({'x':b[0],'y':b[1]+frames[len(records)].info.get('logical_origin_y',0),'w':crop.width,'h':crop.height,'sx':x,'sy':y})
            x+=crop.width;used=max(used,x);row=max(row,crop.height)
        height=y+row
        if height<=4096:layouts.append((used*height,used,height,records))
    if not layouts:raise ValueError('Atlas exceeds supported packing dimensions')
    _,width,height,records=min(layouts,key=lambda layout:(layout[0],layout[2]))
    right=Image.new('RGBA',(width,height));left=right.copy()
    for (_,crop),f in zip(crops,records):
        right.paste(crop,(f['sx'],f['sy']));left.paste(ImageOps.mirror(crop),(f['sx'],f['sy']))
    out.mkdir(parents=True,exist_ok=True)
    for side,im in [('right',right),('left',left)]:im.save(out/(name+'-'+side+'.png'))
    return {'right':name+'-right','left':name+'-left','width':width,'height':height,'frames':records,'decoded_bytes':width*height*8}
def compile(student,out):
    config=read(HERE/'assets/characters.json');manifest=read(HERE/'assets/character-assets.json');student=validate(student,config,manifest)
    key=visual_key(student);record=out/(key+'.json')
    # Digest the authored inputs too; edits to a body invalidate cached previews.
    sources=[Path(__file__),HERE/'tools/skin_palette.py',HERE/'tools/character_registry.py',HERE/'assets/character-assets.json',HERE/'assets/character-masks.json']
    from identity_art import sources as identity_sources,attachments,replace,head
    sources.extend(identity_sources(student))
    from hair_art import sources as hair_sources,styles as hair_styles,apply as apply_hair,logical_bounds
    sources.extend(hair_sources(student))
    for layer in ('body','face','hair','foreground'):
        variant=student[layer] if layer in ('face','hair') else 'default'
        if layer=='hair' and variant in hair_styles():variant='default'
        sources.append(HERE/'src/assets'/(manifest[student['body']]['parts'][layer][variant]['right']+'.png'))
    sources.extend(HERE/'src/assets'/(part['right']+'.png') for part in manifest[student['body']]['parts']['belt'].values())
    signature=[[p.name,p.stat().st_mtime_ns,p.stat().st_size] for p in sources]
    if record.exists():
        cached=read(record)
        if cached.get('signature')==signature:return cached
    body=student['body'];ap=student['appearance'];identity=student.get('identity','default');frames=[Image.new('RGBA',(224,144)) for _ in range(92)]
    for layer in ('body','face','hair','foreground'):
        variant=student[layer] if layer in ('face','hair') else 'default'
        if layer=='hair' and variant in hair_styles():variant='default'
        for i,frame in enumerate(layer_frames(body,layer,variant,manifest)):
            if identity=='default' and layer!='hair':frame=apply_skin_palette(frame,ap['skin'])
            from hair_palette import target as hair_color_target
            hair_target=hair_color_target(ap['hair_color']) if layer=='hair' else None
            skin_target=SKINS[ap['skin']]
            if identity=='default' and hair_target:
                pixels=frame.load();b=frame.getbbox() or (0,0,0,0)
                hair_mask=Image.new('L',frame.size)
                if hair_target:
                    mask=hair_mask.load()
                    for y in range(b[1],b[3]):
                        for x in range(b[0],b[2]):
                            r,g,bl,a=pixels[x,y]
                            if a and max(r,g,bl)>23 and not skin((r,g,bl)):mask[x,y]=255
                    # Protect fine face/gi outlines inside the legacy head layer.
                    hair_mask=hair_mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
                for y in range(b[1],b[3]):
                    for x in range(b[0],b[2]):
                        r,g,bl,a=pixels[x,y]
                        if a and hair_target and hair_mask.getpixel((x,y)) and max(r,g,bl)>23 and not skin((r,g,bl)):
                            light=.35+.65*min(1,max(r,g,bl)/110)
                            pixels[x,y]=(*(min(255,round(c*light)) for c in hair_target),a)
            frames[i].alpha_composite(frame)
    if identity!='default':
        from identity_art import paint
        foreground=layer_frames(body,'foreground','default',manifest)
        bindings=attachments(body)
        frames=[paint(replace(frame,student,bindings[i],foreground[i])[0],student,head(student,bindings[i])) for i,frame in enumerate(frames)]
    if ap['emblem']=='dojo':
        masks=read(HERE/'assets/character-masks.json')[body]
        for i,frame in enumerate(frames):
            # Small D patch on visible white gi only, never over arms, belt or skin.
            region_head=masks[str(i+1)]['head'];x=min(214,max(5,(region_head[0]+region_head[2])//2+7));y=min(133,region_head[3]+7)
            for dx,dy in [(0,0),(1,0),(2,1),(2,2),(2,3),(1,4),(0,4),(0,1),(0,2),(0,3)]:
                r,g,b,a=frame.getpixel((x+dx,y+dy))
                if a and min(r,g,b)>140 and max(r,g,b)-min(r,g,b)<65:frame.putpixel((x+dx,y+dy),(112,54,45,255))
    frames=[transform(apply_hair(f,student,'base',i),ap,manifest[body]['bounds'][i]) for i,f in enumerate(frames)]
    parts={'body':pack(frames,'char-visual-'+key,out),'belt':{}}
    geometry={'height':ap['height'],'build':ap['build']};gkey=visual_key({**student,'face':'default','hair':'default','identity':'default','appearance':geometry})
    for belt in config['belt_order']:
        belt_frames=[transform(f,ap,manifest[body]['bounds'][i]) for i,f in enumerate(layer_frames(body,'belt',belt,manifest))]
        parts['belt'][belt]=pack(belt_frames,'char-geometry-'+gkey+'-'+belt,out)
    # A generated selection portrait; no private photograph enters a package.
    portrait=frames[0].copy()
    portrait_head=read(HERE/'assets/character-masks.json')[body]['1']['head'] if identity=='default' else transform(head(student,attachments(body)[0]),ap,manifest[body]['bounds'][0]).getbbox()
    margins=(12,6,16,30) if identity=='default' else (8,4,8,22)
    padding=portrait.height-144
    portrait=portrait.crop((max(0,portrait_head[0]-margins[0]),max(0,portrait_head[1]+padding-margins[1]-6),min(224,portrait_head[2]+margins[2]),min(portrait.height,portrait_head[3]+padding+margins[3])))
    portrait.thumbnail((32,40),Image.Resampling.NEAREST);thumbnail=Image.new('RGBA',(32,40));thumbnail.paste(portrait,((32-portrait.width)//2,(40-portrait.height)//2));thumbnail.save(out/('portrait-'+key+'.png'))
    result={'id':key,'body':body,'parts':parts,'bounds':[logical_bounds(f) for f in frames],'portrait':'portrait-'+key,'signature':signature,
            'appearance':ap,'identity':identity,'hair':student['hair'],'portrait_bytes':32*40*4,'decoded_bytes':parts['body']['decoded_bytes']+parts['belt'][student['belt']]['decoded_bytes']}
    write(record,result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    try:result=compile(read(a.input),a.out);print(json.dumps(result))
    except (ValueError,KeyError) as e:print(str(e),file=sys.stderr);sys.exit(2)
