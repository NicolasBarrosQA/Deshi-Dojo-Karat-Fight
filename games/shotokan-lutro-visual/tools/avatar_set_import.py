"""Import authored 2D neutral fighters into staged historical image/quad atlases.

No pose synthesis, bone animation, 3D rendering, or deformation. Chroma belt
markers isolate cloth; head area calibrates scale without enlarging tucked jumps.
"""
import argparse, hashlib, json, statistics
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageFont
from compile_character import pack
from character_registry import DEFAULT

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'assets/source/avatar-set-v3'
STAGE = ROOT/'.runtime/avatar-set-v3'
DOCS = ROOT/'docs/avatar-set-v3'
BODIES = {'adult':('adulto-masculino',129), 'teen':('adolescente-masculino',111),
          'child':('crianca-masculina',93), 'adult_female':('adulta-feminina',129),
          'teen_female':('adolescente-feminina',111), 'child_female':('crianca-feminina',93)}
# Authored upright reference cells (zero-based), never a folded jump or kick.
UPRIGHT={'base-01':[0], 'base-10':[2], 'base-19':[5], 'base-28':[1,5],
         'base-37':[3,7], 'base-46':[2,3], 'base-55':[2], 'base-82':[6]}

def read(path):return json.loads(path.read_text(encoding='utf8'))
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def groups(mask):
    """Connected row runs: independent of arbitrary sheet cell boundaries."""
    parents,runs,previous=[],[],[]
    def root(i):
        while parents[i]!=i:
            parents[i]=parents[parents[i]];i=parents[i]
        return i
    for y,row in enumerate(mask):
        edges=np.flatnonzero(np.diff(np.pad(row.astype(np.int8),(1,1))))
        current=[]
        for start,end in zip(edges[::2],edges[1::2]):
            ident=len(parents);parents.append(ident)
            runs.append((y,int(start),int(end),ident))
            for ps,pe,pi in previous:
                if start<=pe and end>=ps:parents[root(ident)]=root(pi)
            current.append((int(start),int(end),ident))
        previous=current
    result={}
    for y,start,end,ident in runs:result.setdefault(root(ident),[]).append((y,start,end))
    return sorted(result.values(),key=lambda rs:sum(e-s for _,s,e in rs),reverse=True)

def area(rs):return sum(e-s for _,s,e in rs)
def box(rs):return (min(s for _,s,_ in rs),min(y for y,_,_ in rs),max(e for _,_,e in rs),max(y for y,_,_ in rs)+1)

def figures(sheet,count=9,cols=3):
    pieces=groups(np.asarray(sheet.getchannel('A'))>=128)[:count]
    if len(pieces)!=count or min(area(rs) for rs in pieces)<1000:
        raise ValueError(f'Expected {count} complete disconnected figures')
    pieces.sort(key=lambda rs:sum(y*(e-s) for y,s,e in rs)/area(rs))
    ordered=[]
    for row in range((count+cols-1)//cols):
        ordered.extend(sorted(pieces[row*cols:(row+1)*cols],key=lambda rs:sum((s+e)*(e-s)/2 for _,s,e in rs)/area(rs)))
    result=[]
    for rs in ordered:
        left,top,right,bottom=box(rs)
        im=sheet.crop((left,top,right,bottom))
        alpha=np.zeros((bottom-top,right-left),dtype=np.uint8)
        for y,s,e in rs:alpha[y-top,s-left:e-left]=255
        im.putalpha(Image.fromarray(alpha));result.append(im)
    return result

def skin_head(im):
    if '_skin_head' in im.info:return im.info['_skin_head']
    px=np.asarray(im).astype(np.int16);r,g,b,a=[px[:,:,i] for i in range(4)]
    mask=(a>0)&(r>g*1.10)&(g>b*1.06)&(r-b>24)&(r>55)
    parts=groups(mask)
    if not parts or area(parts[0])<100:raise ValueError('Cannot identify neutral head; explicit annotation required')
    im.info['_skin_head']=parts[0]
    return parts[0]

def cranial_width(im):
    """Stable upper-head diameter: neck/chest area is not a scale reference."""
    if '_cranial_width' in im.info:return im.info['_cranial_width']
    px=np.asarray(im).astype(np.int16);r,g,b,a=[px[:,:,i] for i in range(4)]
    mask=(a>0)&(r>g*1.10)&(g>b*1.06)&(r-b>24)&(r>55)
    candidates=[p for p in groups(mask) if area(p)>=100 and box(p)[1]<im.height*.4]
    component=max(candidates,key=lambda p:area(p)/(1+20*box(p)[1]/im.height))
    left,top,right,bottom=box(component)
    widths=sorted(end-start for y,start,end in component if y<top+(bottom-top)*.70)
    result=widths[int((len(widths)-1)*.9)];im.info['_cranial_width']=result
    return result

def chroma_belt(im,hidden=False):
    px=np.asarray(im).astype(np.int16);r,g,b,a=[px[:,:,i] for i in range(4)]
    pink=(a>0)&(r>24)&(b>24)&(r>g*1.40)&(b>g*1.20)
    if hidden:return Image.new('L',im.size),pink
    expanded=Image.fromarray((pink*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))
    parts=groups(np.asarray(expanded)>0)
    if not parts:raise ValueError('No magenta belt')
    selected=np.zeros(pink.shape,dtype=bool)
    for y,s,e in parts[0]:selected[y,s:e]=True
    owned=pink&selected
    if owned.sum()<40:raise ValueError('Missing visible belt cloth')
    return Image.fromarray((owned*255).astype(np.uint8)),pink&~selected

def normalize(im,scale,limits=True,belt_hidden=False):
    source_head=skin_head(im)
    belt,stray=chroma_belt(im,belt_hidden)
    px=np.asarray(im).copy();px[stray]=0
    # Remove saturated generation fringe, never natural warm skin.
    r,g,b,a=[px[:,:,i].astype(np.int16) for i in range(4)]
    noise=((r>175)&(g<55)&(b<85))|((r>180)&(g>170)&(b<55))|((b>175)&(r<90)&(g<90))
    m=np.asarray(belt)>0
    px[noise&~m]=0
    # Replace marker RGB before resampling; no pink can bleed into white gi.
    light=np.maximum(px[:,:,0],px[:,:,2])/255
    for c,base in enumerate((238,238,244)):px[:,:,c][m]=np.clip(base*(.48+.52*light[m]),0,255).astype(np.uint8)
    source=Image.fromarray(px)
    size=(round(im.width*scale),round(im.height*scale))
    if limits and (size[0]>210 or size[1]>137):
        raise ValueError(f'Anatomical head scale exceeds cell: {size}; repair source instead of shrinking pose')
    resized=source.resize(size,Image.Resampling.LANCZOS)
    alpha=resized.getchannel('A').point(lambda a:255 if a>=128 else 0)
    resized.putalpha(alpha)
    cloth=belt.resize(size,Image.Resampling.BOX).point(lambda a:255 if a>=32 else 0)
    cloth_np=np.asarray(cloth).copy();cloth_np[np.asarray(alpha)==0]=0;cloth=Image.fromarray(cloth_np)
    bbox=box(source_head);head=tuple(round(v*scale) for v in bbox)
    # Belt centre is the body's origin; extending a fist does not slide the torso.
    ys,xs=np.nonzero(np.asarray(belt));pivot=float(np.median(xs)) if len(xs) else (bbox[0]+bbox[2])/2
    x=round(112-pivot*scale);x=max(0,min(224-size[0],x))
    visible=resized.getbbox()
    if not visible:raise ValueError('Empty normalized figure')
    y=143-visible[3]
    frame=Image.new('RGBA',(224,144));frame.paste(resized,(x,y))
    mask=Image.new('L',(224,144));mask.paste(cloth,(x,y))
    frame=Image.composite(frame,Image.new('RGBA',frame.size),frame.getchannel('A'))
    return frame,mask,{'scale':scale,'head_source_area':area(source_head),
        'head':[head[0]+x,head[1]+y,head[2]+x,head[3]+y],
        'belt':list(mask.getbbox()) if mask.getbbox() else None,'belt_visible':not belt_hidden,'bounds':list(frame.getbbox())}

def jump_cap_center(frame):
    component=skin_head(frame);left,top,right,bottom=box(component)
    cap=[run for run in component if run[0]<top+(bottom-top)*.45]
    l,t,r,b=box(cap)
    return (l+r)/2

def align_jump_transition(frames,masks,entries):
    """Keep the upper body anchored when the rising pose becomes descent."""
    first,second=jump_cap_center(frames[7]),jump_cap_center(frames[8])
    dx=round(first-second)
    bounds=frames[8].getbbox()
    if not 0<=bounds[0]+dx<bounds[2]+dx<=224:raise ValueError('Jump alignment clips the authored pose')
    for images in (frames,masks):
        moved=Image.new(images[8].mode,images[8].size);moved.paste(images[8],(dx,0));images[8]=moved
    for key in ('head','belt','bounds'):
        if entries[8][key]:
            entries[8][key][0]+=dx;entries[8][key][2]+=dx
    entries[8]['jump_transition_shift_x']=dx
    entries[7]['jump_cap_x']=first;entries[8]['jump_cap_x']=second+dx
    return dx

def palettes(frames,masks,name,config,out):
    result={}
    for key,rgb in config['belts'].items():
        values=[]
        for frame,mask in zip(frames,masks):
            px=np.asarray(frame).copy();m=np.asarray(mask)>0
            light=px[:,:,:3].max(axis=2)/244
            for c,base in enumerate(rgb):px[:,:,c][m]=np.clip(base*light[m],0,255).astype(np.uint8)
            px[:,:,3]=np.asarray(mask);px[~m]=0
            values.append(Image.fromarray(px))
        result[key]=pack(values,name+'-'+key,out)
    return result

def separate(frames,masks):
    result=[]
    for frame,mask in zip(frames,masks):
        px=np.asarray(frame).copy();px[np.asarray(mask)>0]=0
        result.append(Image.fromarray(px))
    return result

def main(allow_partial=False,only_body=None):
    jobs=read(SOURCE/'jobs.json');config=read(ROOT/'assets/characters.json')
    missing=[j['target'] for j in jobs if not Path(j['target']).exists()]
    if missing and not allow_partial:raise ValueError(f'{len(missing)} authored sheets missing; not ready to replace characters')
    out=STAGE/'assets';out.mkdir(parents=True,exist_ok=True);DOCS.mkdir(parents=True,exist_ok=True)
    if only_body:
        bodies=read(STAGE/'character-assets.json');specials=read(STAGE/'special-assets.json');annotations=read(STAGE/'character-masks.json')
        previous=read(DOCS/'import-report.json')
        report=[b for b in previous['bodies'] if b['body']!=only_body]
        quality=[q for q in previous['quality_errors'] if q['body']!=only_body]
    else:bodies={};specials={};annotations={};report=[];quality=[]
    allreview={}
    for body,(name,height) in BODIES.items():
        if only_body and body!=only_body:continue
        baseline=SOURCE/body/'base-01.png'
        if not baseline.exists():
            report.append({'body':body,'target_head_area':None,'basic_poses':0,'special_poses':0,'sheets':[]})
            continue
        initial=figures(Image.open(baseline).convert('RGBA'))
        baseline_scale=height/initial[0].height
        target=statistics.median(area(skin_head(f)) for f in initial)*baseline_scale**2
        cranial_target=cranial_width(initial[0])*baseline_scale
        records=[];baseframes=[];basemasks=[];annotations[body]={};specials[body]={};jump_shift=0
        for job in [j for j in jobs if j['body']==body and Path(j['target']).exists()]:
            print('Stage',body,job['group'],flush=True)
            source=Path(job['target'])
            try:
                cells=figures(Image.open(source).convert('RGBA'))
                corrections=SOURCE/'corrections.json'
                if corrections.exists():
                    change=read(corrections).get(body+'/'+job['group'])
                    if change:
                        fixed=figures(Image.open(SOURCE/change['source']).convert('RGBA'))
                        ratio=(area(skin_head(cells[0]))/area(skin_head(fixed[0])))**.5
                        for index in change['cells']:
                            replacement=fixed[index]
                            cells[index]=replacement.resize((round(replacement.width*ratio),round(replacement.height*ratio)),Image.Resampling.LANCZOS)
                cells=cells[:len(job['indices'])]
                if job['group']=='base-01':scale=baseline_scale
                elif not job['group'].startswith('base-') and job['group']!='knockdown':
                    # Special sheets begin in standing guard. Calibrate that
                    # reference once; V-neck visibility in rear views must not
                    # inflate the entire fighter through a skin-area heuristic.
                    scale=height/cells[0].height
                else:scale=(target/statistics.median(area(skin_head(f)) for f in cells))**.5
                if job['group'] in UPRIGHT:
                    refs=UPRIGHT[job['group']]
                    scale=height/statistics.median(cells[i].height for i in refs)
                    page_head=statistics.median(cranial_width(cells[i]) for i in refs)*scale
                elif job['group'].startswith('base-'):
                    page_head=cranial_target
                elif job['group']=='knockdown':
                    page_head=None
                else:
                    page_head=cranial_width(cells[0])*scale
                frames=[];masks=[];entries=[]
                occlusions=read(SOURCE/'occlusions.json') if (SOURCE/'occlusions.json').exists() else {}
                hidden=occlusions.get(body+'/'+job['group'],{}).get('cells',[])
                for i,cell in enumerate(cells):
                    if job['group']=='base-01' or page_head is None:
                        corrected_scale=scale
                    else:
                        corrected_scale=page_head/cranial_width(cell)
                        if job['group'] in UPRIGHT or not job['group'].startswith('base-'):
                            corrected_scale=max(scale*.85,min(scale*1.20,corrected_scale))
                    fitted=min(corrected_scale,137/cell.height,210/cell.width)
                    if fitted/corrected_scale>=.95:corrected_scale=fitted
                    try:frame,mask,entry=normalize(cell,corrected_scale,belt_hidden=i in hidden)
                    except ValueError as error:raise ValueError(f'cell {i+1}: {error}') from error
                    entry.update({'previous_sheet_scale':scale,'cranial_width':cranial_width(cell),'target_cranial_width':page_head,'scale_reference':'upright body and cranial cap; excludes neck and folded legs'})
                    frames.append(frame);masks.append(mask);entries.append(entry)
            except ValueError as error:
                quality.append({'body':body,'group':job['group'],'error':str(error)})
                print('REPAIR REQUIRED',body,job['group'],error,flush=True)
                continue
            group=job['group']
            if group=='base-55':jump_shift=align_jump_transition(frames,masks,entries)
            allreview[(body,group)]=frames
            records.append({'group':group,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frames':entries})
            if group.startswith('base-'):
                baseframes.extend(frames);basemasks.extend(masks)
                for index,entry in zip(job['indices'],entries):annotations[body][str(index+1)]={'head':entry['head'],'belt':entry['belt'],**({'jump_cap_x':entry['jump_cap_x']} if 'jump_cap_x' in entry else {})}
            else:
                specials[body][group]={'body':pack(separate(frames,masks),'special-'+body+'-'+group,out),
                    'belts':palettes(frames,masks,'special-'+body+'-'+group+'-belt',config,out),
                    'bounds':[list(f.getbbox()) for f in frames]}
        if len(baseframes)==92:
            empty=[Image.new('RGBA',(224,144)) for _ in range(92)]
            bodies[body]={'bounds':[list(f.getbbox()) for f in baseframes],'feet_y':142,'revision':'neutral-2d-v3',
                'jump_anchor':{'poses':[62,63],'descent_offset_x':jump_shift,'metric':'cranial-cap-v2','rise_anchor_x':annotations[body]['62']['jump_cap_x'],'descent_anchor_x':annotations[body]['63']['jump_cap_x'],'reference':'Cranial cap centre, excluding angled neck, across rise and descent; facing mirror applies normally.'},
                'parts':{'body':{'default':pack(separate(baseframes,basemasks),'char-'+body+'-body-default',out)},
                    'belt':palettes(baseframes,basemasks,'char-'+body+'-belt',config,out),
                    **{layer:{'default':pack(empty,'char-'+body+'-'+layer+'-default',out)} for layer in ('face','hair','foreground')}}}
            atlas=Image.new('RGBA',(896,3312));maskatlas=Image.new('L',atlas.size)
            for i,(f,m) in enumerate(zip(baseframes,basemasks)):
                atlas.paste(f,((i%4)*224,(i//4)*144));maskatlas.paste(m,((i%4)*224,(i//4)*144))
            atlas.save(STAGE/(body+'-atlas.png'));maskatlas.save(STAGE/(body+'-belt-mask.png'))
        report.append({'body':body,'target_head_area':target,'basic_poses':len(baseframes),'special_poses':sum(len(a['bounds']) for a in specials[body].values()),'sheets':records})
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
    for group in dict.fromkeys(j['group'] for j in jobs):
        image=Image.new('RGB',(224*9,180*6),'#e6e8ee')
        for row,body in enumerate(BODIES):
            ImageDraw.Draw(image).text((4,row*180+2),body+' / '+group,font=font,fill='#172033')
            for i,f in enumerate(allreview.get((body,group),[])):image.paste(f,(224*i,row*180+30),f)
        image.resize((4032,2160),Image.Resampling.NEAREST).save(DOCS/(group+'-review.png'))
    write(STAGE/'character-assets.json',bodies);write(STAGE/'special-assets.json',specials);write(STAGE/'character-masks.json',annotations)
    write(DOCS/'import-report.json',{'missing_sheets':missing,'quality_errors':quality,'bodies':report,'staged_only':True,'generator':'built-in image_gen','runtime':'historical 2D image/quad, no 3D'})
    print(f'Staged {sum(b["basic_poses"]+b["special_poses"] for b in report)} poses; {len(missing)} sheets pending. Game untouched.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--partial',action='store_true');p.add_argument('--body',choices=list(BODIES));a=p.parse_args();main(a.partial,a.body)
