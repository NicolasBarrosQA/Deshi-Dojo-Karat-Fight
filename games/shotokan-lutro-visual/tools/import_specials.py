"""Mechanical sprite ownership, fixed row scale, semantic cloth masks and packing.
Artwork is generated separately; this tool never synthesizes fighter poses.
"""
import argparse,json,shutil
from pathlib import Path
from PIL import Image,ImageOps,ImageFilter
from sheet_cells import figures
from character_masks import components
from compile_character import pack,skin,shade,transform
from character_registry import SKINS,HAIR_COLORS
HERE=Path(__file__).resolve().parents[1]

def masks(im,lying=False):
    w,h=im.size;dark=Image.new('L',im.size)
    for y in range(h):
        for x in range(w):
            r,g,b,a=im.getpixel((x,y))
            if a and max(r,g,b)<105:dark.putpixel((x,y),255)
    core=dark.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    groups=components(core)
    # The reference artwork has black hair at the head and thick cloth at waist.
    cx,cy=(w*.52,h*.50) if lying else (w*.49,h*.55)
    candidates=[p for p in groups if len(p)>10 and (lying or sum(i//w for i in p)/len(p)>h*.32)]
    if not candidates:raise ValueError('No belt cloth interior')
    chosen=min(candidates,key=lambda p:abs(sum(i%w for i in p)/len(p)-cx)*.4+abs(sum(i//w for i in p)/len(p)-cy)-min(len(p),1000)*.018)
    result=Image.new('L',im.size)
    for i in chosen:result.putpixel((i%w,i//w),255)
    expanded=result.filter(ImageFilter.MaxFilter(3))
    for y in range(h):
        for x in range(w):
            if expanded.getpixel((x,y)) and dark.getpixel((x,y)):result.putpixel((x,y),255)
    return result

def run(group,source):
    out=HERE/'src/assets';original=HERE/'assets/source/specials'/f'{group}.png';original.parent.mkdir(parents=True,exist_ok=True)
    if source.resolve()!=original.resolve():shutil.copy2(source,original)
    cells=figures(Image.open(original).convert('RGBA'),9,3,strict=False)
    config=json.loads((HERE/'assets/characters.json').read_text(encoding='utf8'))
    manifest_path=HERE/'assets/special-assets.json';manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for row,body in enumerate(('adult','teen','child')):
        inputs=cells[row*9:row*9+9]
        if group=='knockdown':inputs=[ImageOps.mirror(im) if i in (4,5) else im for i,im in enumerate(inputs)]
        ratio={'adult':129,'teen':111,'child':93}[body]/inputs[0].height
        ratio=min(ratio,142/max(im.height for im in inputs),210/max(im.width for im in inputs))
        frames=[];belts=[]
        for i,im in enumerate(inputs):
            mask=masks(im,group=='knockdown' and i in (3,4,5,6))
            # Clear saturated generation fringe pixels, never interpolate edges.
            px=im.load()
            for y in range(im.height):
                for x in range(im.width):
                    r,g,b,a=px[x,y]
                    if (r>175 and g<40 and b<70) or (b>175 and r<90 and g<90) or (r>170 and b>170 and g<90):px[x,y]=(0,0,0,0);mask.putpixel((x,y),0)
            target=(round(im.width*ratio),round(im.height*ratio))
            resized=im.resize(target,Image.Resampling.NEAREST);cloth=mask.resize(target,Image.Resampling.NEAREST)
            frame=Image.new('RGBA',(224,144));belt=frame.copy()
            x=112-target[0]//2;y=143-target[1];frame.paste(resized,(x,y));belt.paste(resized,(x,y));whole=Image.new('L',(224,144));whole.paste(cloth,(x,y));belt.putalpha(whole)
            frame.putalpha(Image.frombytes('L',frame.size,bytes(0 if m else a for a,m in zip(frame.getchannel('A').tobytes(),whole.tobytes()))))
            frames.append(frame);belts.append(belt)
        record={'body':pack(frames,f'special-{body}-{group}',out),'belts':{},'bounds':[list(Image.alpha_composite(a,b).getbbox()) for a,b in zip(frames,belts)]}
        for name,rgb in config['belts'].items():
            colored=[]
            for belt in belts:
                im=belt.copy();px=im.load()
                for y in range(144):
                    for x in range(224):
                        r,g,b,a=px[x,y]
                        if a and name!='preta':
                            light=.36+.64*min(1,max(r,g,b)/105);px[x,y]=(*(min(255,round(c*light)) for c in rgb),a)
                colored.append(im)
            record['belts'][name]=pack(colored,f'special-{body}-{group}-belt-{name}',out)
        manifest.setdefault(body,{})[group]=record
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Imported',group,'27 poses, fixed scale, 8 cloth palettes')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('group');p.add_argument('source',type=Path);a=p.parse_args();run(a.group,a.source)
