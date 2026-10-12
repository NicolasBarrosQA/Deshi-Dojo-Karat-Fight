"""Import authored female art without altering any existing body or combat rule."""
import json,statistics,argparse
from pathlib import Path
from PIL import Image,ImageOps
from sheet_cells import figures
from character_masks import belt_mask,hair_bounds
from import_characters import binary,regions,split
from import_specials import masks as special_mask
from compile_character import pack
from character_registry import read,write,DEFAULT
HERE=Path(__file__).resolve().parents[1];OUT=HERE/'src/assets';SOURCE=HERE/'assets/source/female'
AGES=('adult','teen','child')
def original_part(part,i):
    r=part['frames'][i]
    with Image.open(OUT/(part['right']+'.png')) as a:
        out=Image.new('RGBA',(224,144));out.paste(a.crop((r['sx'],r['sy'],r['sx']+r['w'],r['sy']+r['h'])),(r['x'],r['y']));return out
def clean(im):
    im=binary(im)
    # Saturated isolated generation fringes are not part of gi, skin or belt.
    p=im.load()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=p[x,y]
            if a and ((r>175 and g<65 and b<95) or (r>180 and g>170 and b<55) or (r>160 and b>140 and g<85) or (b>175 and r<90 and g<90)):p[x,y]=(0,0,0,0)
    return im
def collect(name):
    cells=figures(clean(Image.open(SOURCE/(name+'.png')).convert('RGBA')),9,3,strict=False)
    correction=SOURCE/'corrections.json'
    if correction.exists() and name in read(correction):
        entry=read(correction)[name];fixed=figures(clean(Image.open(SOURCE/entry['source']).convert('RGBA')),9,3,strict=False)
        for i in entry['cells']:
            row=i//9;ratio=cells[row*9].height/fixed[row*9].height
            cells[i]=binary(fixed[i].resize((round(fixed[i].width*ratio),round(fixed[i].height*ratio)),Image.Resampling.NEAREST))
    return cells
def place(inputs,originals):
    ratio=statistics.median((o.getbbox()[3]-o.getbbox()[1])/f.height for o,f in zip(originals,inputs))
    ratio=min(ratio,137/max(f.height for f in inputs),210/max(f.width for f in inputs))
    assert ratio<=1,'Authored source is too small; never upscale body art'
    frames=[]
    for im,old in zip(inputs,originals):
        size=(round(im.width*ratio),round(im.height*ratio));im=binary(im.resize(size,Image.Resampling.NEAREST))
        box=old.getbbox();cx=(box[0]+box[2])/2
        x=max(0,min(224-size[0],round(cx-size[0]/2)));y=143-size[1]
        f=Image.new('RGBA',(224,144));f.paste(im,(x,y));frames.append(f)
    return frames
def belts(frames,masks,config,name):
    cloth=[]
    for frame,mask in zip(frames,masks):
        im=frame.copy();im.putalpha(mask);cloth.append(im)
    result={}
    for key,rgb in config['belts'].items():
        painted=[]
        for frame in cloth:
            im=frame.copy();p=im.load()
            if key!='preta':
                box=im.getbbox() or (0,0,0,0)
                for y in range(box[1],box[3]):
                    for x in range(box[0],box[2]):
                        r,g,b,a=p[x,y]
                        if a:p[x,y]=(*(round(c*(.48+.52*min(1,max(r,g,b)/100))) for c in rgb),255)
            painted.append(im)
        result[key]=pack(painted,name+'-'+key,OUT)
    return result
def main(special_only=None):
    config=read(HERE/'assets/characters.json');manifest=read(HERE/'assets/character-assets.json');annotations=read(HERE/'assets/character-masks.json');special=read(HERE/'assets/special-assets.json')
    allframes={age:[] for age in AGES}
    oldatlases={age:Image.open(HERE/'docs'/f'character-{age}-atlas.png').convert('RGBA') for age in AGES}
    for start in ([] if special_only else range(0,92,9)):
        print('Import basic sheet',start+1,flush=True)
        cells=collect(f'base-{start+1:02d}')
        for row,age in enumerate(AGES):
            indices=list(range(start,min(start+9,92)))
            originals=[oldatlases[age].crop(((i%4)*224,(i//4)*144,(i%4+1)*224,(i//4+1)*144)) for i in indices]
            allframes[age].extend(place(cells[row*9:row*9+len(indices)],originals))
    for age in (() if special_only else AGES):
        print('Pack female base',age,flush=True)
        body=age+'_female';frames=allframes[age];annotations[body]={};layers={k:[] for k in ('body','face','hair','foreground')};cloth=[]
        atlas=Image.new('RGBA',(896,3312));cloth_atlas=Image.new('L',atlas.size)
        for i,f in enumerate(frames):
            region=regions(f);hair=hair_bounds(f)
            # Include the authored tied hair, not just a square around the face.
            region['head']=[min(region['head'][0],hair[0]),region['head'][1],max(region['head'][2],hair[2]),max(region['head'][3],hair[3])]
            annotations[body][str(i+1)]=region;mask=belt_mask(f);cloth.append(mask)
            separated=split(f,region,mask)
            for layer in layers:layers[layer].append(separated[layer])
            atlas.paste(f,((i%4)*224,(i//4)*144));cloth_atlas.paste(mask,((i%4)*224,(i//4)*144))
        previous=manifest.get(body,{})
        manifest[body]={'bounds':[list(f.getbbox()) for f in frames],'feet_y':142,'parts':{layer:{'default':pack(values,f'char-{body}-{layer}-default',OUT)} for layer,values in layers.items()}}
        for layer in ('face','hair'):
            for key,part in previous.get('parts',{}).get(layer,{}).items():
                if key!='default':manifest[body]['parts'][layer][key]=part
        manifest[body]['parts']['belt']=belts(frames,cloth,config,f'char-{body}-belt')
        atlas.save(HERE/'docs'/f'character-{body}-atlas.png');cloth_atlas.save(HERE/'assets'/f'character-belt-{body}-mask.png')
        if body not in config['body_order']:config['body_order'].append(body)
    for group in special['adult']:
        if special_only and group!=special_only:continue
        print('Import female special',group,flush=True)
        cells=collect(group)
        for row,age in enumerate(AGES):
            body=age+'_female';old=special[age][group]
            originals=[Image.alpha_composite(original_part(old['body'],i),original_part(old['belts']['preta'],i)) for i in range(9)]
            frames=place(cells[row*9:(row+1)*9],originals);cloth=[];without=[]
            for i,frame in enumerate(frames):
                bbox=frame.getbbox();crop=frame.crop(bbox);mask=special_mask(crop,group=='knockdown' and i in (3,4,5,6));whole=Image.new('L',frame.size);whole.paste(mask,bbox[:2]);cloth.append(whole)
                im=frame.copy();im.putalpha(Image.frombytes('L',im.size,bytes(0 if m else a for a,m in zip(im.getchannel('A').tobytes(),whole.tobytes()))));without.append(im)
            special.setdefault(body,{})[group]={'body':pack(without,f'special-{body}-{group}',OUT),'belts':belts(frames,cloth,config,f'special-{body}-{group}-belt'),'bounds':[list(f.getbbox()) for f in frames]}
    for age,name in zip(AGES,('Adulta Feminina','Adolescente Feminina','Crianca Feminina')):
        key='demo-'+age+'-female'
        config['students'].setdefault(key,{'id':key,'name':name,'nickname':'Base feminina','body':age+'_female','belt':'preta','face':'default','hair':'default','appearance':DEFAULT.copy()})
    config['student_order']=list(config['students'])
    write(HERE/'assets/character-assets.json',manifest);write(HERE/'assets/character-masks.json',annotations);write(HERE/'assets/special-assets.json',special);write(HERE/'assets/characters.json',config)
    print('Imported three female bases: 276 base poses and 216 special poses. Existing bases unchanged.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--special');a=p.parse_args();main(a.special)
