"""Mechanical binary-alpha import, mask separation and palette packing.

Authored adult, adolescent and child art remains in source/. No deformation,
procedural body drawing or resizing of adult into another age group.
Pillow is required only by this developer import step, never to play/build.
"""
from pathlib import Path
import argparse,hashlib, json, statistics
from PIL import Image, ImageOps
from sheet_cells import figures
from character_masks import hair_bounds,belt_mask

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / 'src/assets'
W, H, COUNT = 224, 144, 92

def lua(v):
    if isinstance(v, str): return json.dumps(v, ensure_ascii=False)
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, (int, float)): return str(v)
    if isinstance(v, list): return '{' + ','.join(lua(x) for x in v) + '}'
    if isinstance(v, dict): return '{' + ','.join('['+lua(k)+']='+lua(x) for k,x in v.items()) + '}'
    raise TypeError(v)

def binary(im):
    im = im.convert('RGBA')
    im.putalpha(im.getchannel('A').point(lambda a: 255 if a >= 128 else 0))
    # Clear RGB of transparent pixels too: tools may otherwise show color ghosts.
    clean = Image.new('RGBA', im.size)
    clean.paste(im, mask=im.getchannel('A'))
    return clean

def imported(body,source_report=None):
    if body.endswith('_female'):
        # Female poses have their own authored/imported atlas, never a resized male.
        path=HERE/'docs'/f'character-{body}-atlas.png'
        atlas=Image.open(path).convert('RGBA')
        frames=[atlas.crop(((i%4)*W,(i//4)*H,(i%4+1)*W,(i//4+1)*H)) for i in range(COUNT)]
        if source_report is not None:source_report.append({'file':str(path.relative_to(HERE)),'poses':COUNT,'scale':1,'upscaled':False})
        return frames
    if body == 'adult':
        frames=[Image.open(OUT / f'pose-{i:02d}.png').convert('RGBA') for i in range(1, COUNT+1)]
        # Preserve native adult anatomy: hair width is not a body scale measurement.
        if source_report is not None:source_report.append({'file':'src/assets/pose-01..92.png','poses':92,'scale':1,'upscaled':False})
        return frames
    layout_path=HERE/'assets/character-source-layout.json'
    groups=[]
    if layout_path.exists():
        layout=json.loads(layout_path.read_text())
        for source in layout['bodies'][body]:
            path=HERE/'assets/source'/source['file'];sheet=binary(Image.open(path))
            print('Importing',body,source['file'],flush=True)
            cells=figures(sheet,source['cols'],source['rows'])
            assert statistics.median(c.height for c in cells)>=160,(body,source['file'],'source too small')
            scale={'teen':112,'child':94}[body]/statistics.median(c.height for c in cells)
            if source.get('airborne'):
                # Tucked knees shorten the figure without shortening the person.
                # Match head width to standing art, never normalize by bent height.
                def head(f,s):
                    native=binary(f.resize((round(f.width*s),round(f.height*s)),Image.Resampling.NEAREST))
                    b=hair_bounds(native);return b[2]-b[0]
                base_cells,base_scale=groups[0]
                target=statistics.median(head(f,base_scale) for f in base_cells[:4])
                scale=groups[-1][1]
                for _ in range(3):
                    actual=statistics.median(head(f,scale) for f in cells[:4])
                    if abs(actual/target-1)<=.03:break
                    scale*=target/actual
            assert scale<=1,(body,source['file'],'never upscale sprite sources')
            scale=min(scale,140/max(c.height for c in cells))
            groups.append((cells,scale))
            if source_report is not None:source_report.append({'file':source['file'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'poses':len(cells),'median_source_height':statistics.median(c.height for c in cells),'scale':scale,'upscaled':False})
    else:
        sheet = binary(Image.open(HERE / 'assets/source' / f'{body}-sheet.png'))
        cells=[]
        for row in range(23):
            for col in range(4):
                cell=sheet.crop((round(col*sheet.width/4),round(row*sheet.height/23),
                                round((col+1)*sheet.width/4),round((row+1)*sheet.height/23)))
                bounds=cell.getbbox();assert bounds,(body,row,col,'empty pose');cells.append(cell.crop(bounds))
        groups=[(cells,{'teen':112,'child':94}[body]/statistics.median(c.height for c in cells[:60]))]
    cells=[(cell,scale) for group,scale in groups for cell in group]
    assert len(cells)==COUNT,(body,'pose count')
    result=[]
    for i,(cell,scale) in enumerate(cells):
        cell=cell.resize((round(cell.width*scale),round(cell.height*scale)),Image.Resampling.NEAREST)
        assert cell.width<=W and cell.height<=140,(body,i,'clipping')
        # Transfer the original pose's belt-relative extension, not its bbox center.
        original=Image.open(OUT/f'pose-{i+1:02d}.png').getbbox()
        adult_center=(original[0]+original[2])/2
        relative=(adult_center-112)*({'teen':112,'child':94}[body]/128)
        x=round(112+relative-cell.width/2);y=143-cell.height
        assert x>=0 and x+cell.width<=W,(body,i,'clipping')
        frame=Image.new('RGBA',(W,H));frame.paste(cell,(x,y));result.append(frame)
    return result

def regions(frame):
    """Locate attachment regions; per-pose overrides are editable in masks.json."""
    b=frame.getbbox();bh=b[3]-b[1]
    hair=[]
    for y in range(b[1], b[1]+max(6,round(bh*.16))):
        for x in range(b[0],b[2]):
            r,g,bl,a=frame.getpixel((x,y))
            if a and max(r,g,bl)<105: hair.append((x,y))
    cx=round(statistics.mean(x for x,y in hair)) if hair else 112
    head_h=max(18,round(bh*.24));head_w=max(18,round(bh*.24))
    head=[cx-head_w//2,b[1],cx+head_w//2+1,b[1]+head_h]
    rows=[]
    for y in range(b[1]+round(bh*.40),b[1]+round(bh*.68)):
        xs=[x for x in range(90,135) if frame.getpixel((x,y))[3] and max(frame.getpixel((x,y))[:3])<80]
        if xs: rows.append((len(xs),y))
    belt_y=max(rows)[1] if rows else b[1]+round(bh*.52)
    return {'head':head,'belt':[86,belt_y-4,140,min(142,belt_y+22)]}

def split(frame,regions,cloth_mask=None):
    parts={k:Image.new('RGBA',frame.size) for k in ('body','belt','face','hair','foreground')}
    head,belt=regions['head'],regions['belt']
    for y in range(H):
        for x in range(W):
            pixel=frame.getpixel((x,y));r,g,b,a=pixel
            if not a:continue
            layer='body'
            if head[0]<=x<head[2] and head[1]<=y<head[3]:
                if max(r,g,b)<110:layer='hair'
                elif r>g*1.12 and g>b*1.12:layer='face'
                else:layer='foreground'
            if cloth_mask is not None:
                if cloth_mask.getpixel((x,y)):layer='belt'
            elif belt[0]<=x<belt[2] and belt[1]<=y<belt[3] and max(r,g,b)<100:layer='belt'
            for rect in regions.get('foreground',[]):
                if rect[0]<=x<rect[2] and rect[1]<=y<rect[3]:layer='foreground'
            parts[layer].putpixel((x,y),pixel)
    return parts

def pack(body,layer,variant,frames):
    crops=[];records=[]
    for frame in frames:
        b=frame.getbbox() or (0,0,1,1)
        crops.append(frame.crop(b));records.append({'x':b[0],'y':b[1],'w':b[2]-b[0],'h':b[3]-b[1]})
    cw=max(im.width for im in crops);ch=max(im.height for im in crops)
    size=(cw*4,ch*23);right=Image.new('RGBA',size);left=Image.new('RGBA',size)
    for i,(crop,record) in enumerate(zip(crops,records)):
        sx=(i%4)*cw;sy=(i//4)*ch;record.update(sx=sx,sy=sy)
        right.paste(crop,(sx,sy));left.paste(ImageOps.mirror(crop),(sx,sy))
    name=f'char-{body}-{layer}-{variant}'
    right.save(OUT/(name+'-right.png'));left.save(OUT/(name+'-left.png'))
    return {'right':name+'-right','left':name+'-left','width':size[0],'height':size[1],'frames':records,
            'decoded_bytes':size[0]*size[1]*8}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-masks',action='store_true',help='Re-anchor generated child/teen masks for replacement art')
    parser.add_argument('--refresh-belt-masks',action='store_true',help='Regenerate exact cloth pixel masks for visual review')
    parser.add_argument('--repack',action='store_true',help='Repack existing imported poses after cloth-mask annotations, without scaling them again')
    args=parser.parse_args()
    data=json.loads((HERE/'assets/characters.json').read_text(encoding='utf-8'))
    masks_path=HERE/'assets/character-masks.json'
    masks=json.loads(masks_path.read_text()) if masks_path.exists() else {}
    manifest_path=HERE/'assets/character-assets.json'
    previous=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    cloth_overrides_path=HERE/'assets/character-belt-overrides.json'
    cloth_overrides=json.loads(cloth_overrides_path.read_text()) if cloth_overrides_path.exists() else {}
    previous_report=json.loads((HERE/'assets/character-import.json').read_text()) if args.repack else {}
    data['bodies']={};report={'poses':COUNT,'bases':{},'art_tool':'built-in image_gen',
        'notes':'Binary alpha >=128; uniform scale within independently authored bases. Pose identity/technique requires instructor review.'}
    for body in data['body_order']:
        source_report=[]
        if args.repack:
            imported_atlas=Image.open(HERE/'docs'/f'character-{body}-atlas.png').convert('RGBA')
            frames=[imported_atlas.crop(((i%4)*W,(i//4)*H,(i%4+1)*W,(i//4+1)*H)) for i in range(COUNT)]
            source_report=previous_report.get('bases',{}).get(body,{}).get('sources',[{'file':f'docs/character-{body}-atlas.png','poses':COUNT,'scale':1,'upscaled':False}])
        else:frames=imported(body,source_report)
        correction_path=HERE/'assets/pose-corrections.json'
        if correction_path.exists():
            for pose,path in json.loads(correction_path.read_text()).get(body,{}).items():frames[int(pose)-1]=binary(Image.open(HERE/path))
        masks.setdefault(body,{})
        cloth_path=HERE/'assets'/f'character-belt-{body}-mask.png'
        cloth_atlas=Image.open(cloth_path).convert('L') if cloth_path.exists() and not args.refresh_belt_masks else Image.new('L',(896,3312))
        refresh_cloth=args.refresh_belt_masks or not cloth_path.exists()
        layers={k:[] for k in ('body','belt','face','hair','foreground')}
        for i,frame in enumerate(frames):
            if args.refresh_masks and (body!='adult' or 60<=i<76):
                new_region=regions(frame)
                if 'foreground' in masks[body].get(str(i+1),{}):new_region['foreground']=masks[body][str(i+1)]['foreground']
                masks[body][str(i+1)]=new_region
            region=masks[body].setdefault(str(i+1),regions(frame))
            if refresh_cloth:
                cloth=belt_mask(binary(frame),cloth_overrides.get(body,{}).get(str(i+1)));cloth_atlas.paste(cloth,((i%4)*W,(i//4)*H))
            else:cloth=cloth_atlas.crop(((i%4)*W,(i//4)*H,(i%4+1)*W,(i//4+1)*H))
            parts=split(frame,region,cloth)
            for k,v in parts.items():layers[k].append(v)
            rebuilt=Image.new('RGBA',frame.size)
            for v in parts.values():rebuilt.alpha_composite(v)
            assert rebuilt.tobytes()==binary(frame).tobytes(),(body,i,'partition mismatch')
        b={'bounds':[list(f.getbbox()) for f in frames],'feet_y':142,'parts':{}}
        for layer in ('body','face','hair','foreground'):
            b['parts'][layer]={'default':pack(body,layer,'default',layers[layer])}
        b['parts']['belt']={}
        for belt,rgb in data['belts'].items():
            colored=[]
            for frame in layers['belt']:
                im=frame.copy()
                if belt!='preta':
                    bounds=im.getbbox() or (0,0,0,0)
                    for y in range(bounds[1],bounds[3]):
                        for x in range(bounds[0],bounds[2]):
                            r,g,bl,a=im.getpixel((x,y))
                            if a:
                                shade=.48+.52*min(1,max(r,g,bl)/100)
                                im.putpixel((x,y),tuple(round(c*shade) for c in rgb)+(255,))
                colored.append(im)
            b['parts']['belt'][belt]=pack(body,'belt',belt,colored)
        for layer in ('face','hair'):
            for key,part in previous.get(body,{}).get('parts',{}).get(layer,{}).items():
                if key!='default':b['parts'][layer][key]=part
        data['bodies'][body]=b
        cloth_atlas.save(cloth_path)
        selected=sum(b['parts'][k]['preta' if k=='belt' else 'default']['decoded_bytes'] for k in layers)
        report['bases'][body]={'frames':len(frames),'bounds':b['bounds'],'one_selected_character_bytes':selected,'sources':source_report}
        # Reconstruct an inspectable contact sheet at actual game scale.
        atlas=Image.new('RGBA',(896,3312))
        for i,frame in enumerate(frames):atlas.paste(frame,((i%4)*W,(i//4)*H))
        atlas.save(HERE/'docs'/f'character-{body}-atlas.png')
    (HERE/'src/character_data.lua').write_text('return '+lua(data)+'\n',encoding='utf-8')
    (HERE/'assets/character-assets.json').write_text(json.dumps(data['bodies'],indent=2)+'\n')
    (HERE/'assets/character-masks.json').write_text(json.dumps(masks,indent=2)+'\n')
    (HERE/'assets/character-import.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:{x:y for x,y in v.items() if x!='bounds'} for k,v in report['bases'].items()},indent=2))

if __name__=='__main__':main()
