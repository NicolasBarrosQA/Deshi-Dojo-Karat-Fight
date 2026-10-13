"""Offline skull registration and pixel-exact pose layers for the approved cuts.

Legacy centres seed the search, never define the size of the new hairstyle.
The target is registered against the actual source skull cap, excluding hands.
The result is stored per pose: runtime has no tracking or hair transformations.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from prepare_hair_bindings import animations
from head_registration import skin_mask
from native_hair_material import extract
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets/source/hair-rebuild-v2';OUT=ROOT/'assets/native-hair-v2';DOC=ROOT/'docs/hair-rebuild-v2'
ORDER=['adult','teen','child','adult_female','teen_female','child_female']
STYLES=['masculino_curto','feminino_chanel'];PAD=24

def foreground(binding):
    mask=np.zeros((144,224),dtype=bool)
    for y,a,b in binding.get('foreground_runs',[]):mask[y,a:b]=True
    for x,y in binding.get('foreground_points',[]):mask[y,x]=True
    return mask

def rotation(angle):
    a=math.radians(angle)
    return np.array([[math.cos(a),math.sin(a)],[-math.sin(a),math.cos(a)]])

def cap(frame,center,angle,protect):
    yy,xx=np.indices((144,224));p=np.stack([xx-center[0],yy-center[1]],axis=-1)@rotation(angle)
    # Full crown/temple outline, bounded away from neck, feet and nearby fists.
    return skin_mask(frame)&~protect&(abs(p[:,:,0])<15)&(p[:,:,1]>-19)&(p[:,:,1]<5)&((p[:,:,0]/16)**2+(p[:,:,1]/19)**2<1)

def register(frame,binding,reference,refbinding):
    c=np.array(binding['center']);rc=np.array(refbinding['center']);angle=binding.get('angle',0)-refbinding.get('angle',0)
    src=cap(reference,rc,refbinding.get('angle',0),foreground(refbinding));target=cap(frame,c,binding.get('angle',0),foreground(binding))
    sy,sx=np.where(src);points=np.stack([sx,sy],axis=1)-rc
    ty,tx=np.where(target);targetpoints=np.stack([tx,ty],axis=1)
    best=None
    for scale in (.9,1.,1.1):
        for delta in (-8,0,8):
            a=rotation(angle+delta);local=points@a.T*scale
            for dx in (-2,-1,0,1,2):
                for dy in (-2,-1,0,1,2):
                    center=c+[dx,dy];mapped=np.rint(local+center).astype(int)
                    valid=(mapped[:,0]>=0)&(mapped[:,0]<224)&(mapped[:,1]>=0)&(mapped[:,1]<144);mapped=mapped[valid]
                    mask=np.zeros_like(target);mask[mapped[:,1],mapped[:,0]]=True
                    union=np.count_nonzero(mask|target);overlap=np.count_nonzero(mask&target)
                    score=overlap/max(1,union)-.005*(abs(dx)+abs(dy))-.03*abs(scale-1)-.0005*abs(delta)
                    if best is None or score>best[0]:best=(score,center,scale,angle+delta)
    score,center,scale,angle=best
    return {'center':[round(float(v),2) for v in center],'scale':scale,'angle':round(float(angle),2),'skull_iou':round(float(score),4),'reference_center':rc.tolist()}

def warp(hair,fit,origin):
    # Inverse affine directly samples the native source grid without blur.
    a=rotation(fit['angle'])*fit['scale'];inverse=np.linalg.inv(a)
    source_anchor=np.array(fit['reference_center'])-np.array(origin)
    target_anchor=np.array(fit['center'])+[0,PAD]
    offset=source_anchor-inverse@target_anchor
    matrix=(*inverse[0],float(offset[0]),*inverse[1],float(offset[1]))
    return hair.transform((224,144+PAD),Image.Transform.AFFINE,matrix,Image.Resampling.NEAREST)

def seal_crown(layer,frame,fit,protect):
    """Seal one-texel sampling cracks on the scalp, never extend onto the face."""
    yy,xx=np.indices((144,224));dx=xx-fit['center'][0];dy=yy-fit['center'][1]
    local=np.stack([dx,dy],axis=-1)@rotation(fit['angle'])
    scalp=skin_mask(frame)&~protect&(abs(local[:,:,0])<7)&(local[:,:,1]<-4)&(local[:,:,1]>-22)
    if not scalp.any():return layer,0
    # Top three authored skin rows in head-local coordinates are crown, not jaw.
    top=float(local[:,:,1][scalp].min());scalp&=local[:,:,1]<top+3
    pixels=np.asarray(layer).copy();visible=pixels[PAD:,:,3]>0;count=0
    for y,x in zip(*np.where(scalp&~visible)):
        candidates=[(dy*dy+dx*dx,y+dy,x+dx) for dy in range(-1,2) for dx in range(-1,2) if 0<=y+dy<144 and 0<=x+dx<224 and visible[y+dy,x+dx]]
        if candidates:
            _,ny,nx=min(candidates);pixels[y+PAD,x]=pixels[ny+PAD,nx];count+=1
    return Image.fromarray(pixels),count

def clean_material(image,anchor):
    """Exclude tagged background halos outside the authored scalp/nape region."""
    pixels=np.asarray(image).copy();yy,xx=np.indices(pixels.shape[:2])
    roi=(abs(xx-anchor[0])<=25)&(yy>=anchor[1]-25)&(yy<=anchor[1]+24)
    mask=(pixels[:,:,3]>0)&roi;seen=np.zeros_like(mask);components=[]
    for y,x in zip(*np.where(mask)):
        if seen[y,x]:continue
        todo=[(y,x)];seen[y,x]=True;component=[]
        while todo:
            py,px=todo.pop();component.append((py,px))
            for dy,dx in ((0,1),(0,-1),(1,0),(-1,0),(-1,-1),(-1,1),(1,-1),(1,1)):
                ny,nx=py+dy,px+dx
                if 0<=ny<64 and 0<=nx<64 and mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;todo.append((ny,nx))
        components.append(component)
    assert components,'Missing hair material'
    keep=np.zeros_like(mask)
    for y,x in max(components,key=len):keep[y,x]=True
    pixels[~keep]=0
    return Image.fromarray(pixels)

def main(reuse_registration=False):
    OUT.mkdir(exist_ok=True);poses=animations();bindings=json.loads((ROOT/'assets/hair-bindings.json').read_text())
    front=json.loads((SRC/'guard-reference-landmarks.json').read_text());rear=json.loads((SRC/'rear-reference-landmarks.json').read_text())
    result={'version':1,'logical_origin_y':-PAD,'styles':{}};fits={};sources={}
    if reuse_registration:fits=json.loads((DOC/'native-pose-registration.json').read_text())
    for body in ([] if reuse_registration else ORDER):
        fits[body]={}
        for group,frames in poses[body].items():
            fits[body][group]=[]
            for index,frame in enumerate(frames):
                b=bindings[body][group][index];view='rear' if b['view'].startswith('rear') else 'front';ri=57 if view=='rear' else 0
                fit=register(frame,b,poses[body]['base'][ri],bindings[body]['base'][ri])
                if group=='base' and index==ri:fit.update(center=b['center'],scale=1.,angle=0.,skull_iou=1.)
                fit['view']=view;fits[body][group].append(fit)
    for style in STYLES:
        result['styles'][style]={}
        for view in ('front','rear'):
            paint=Image.open(SRC/(style+('-six-rear-heads.png' if view=='rear' else '-six-heads.png'))).convert('RGBA')
            assert paint.size==(1536,1024),'Reference grid changed'
            for i,body in enumerate(ORDER):
                raw=paint.crop((i%3*512,i//3*512,(i%3+1)*512,(i//3+1)*512)).resize((64,64),Image.Resampling.NEAREST)
                origin=np.array((rear if view=='rear' else front)[body])-[32,28]
                ri=57 if view=='rear' else 0
                anchor=np.array(bindings[body]['base'][ri]['center'])-origin
                sources[style,body,view]=clean_material(extract(raw,'original'),anchor)
        for body in ORDER:
            atlas=Image.new('RGBA',(64*14,64*13));entries={};count=0
            review=Image.new('RGB',(120*14,150*13),'#263c49');draw=ImageDraw.Draw(review)
            for group,frames in poses[body].items():
                entries[group]=[]
                for index,frame in enumerate(frames):
                    fit=fits[body][group][index];view=fit['view'];anchor=(rear if view=='rear' else front)[body];origin=[anchor[0]-32,anchor[1]-28]
                    layer=warp(sources[style,body,view],fit,origin)
                    layer,sealed=seal_crown(layer,frame,fit,foreground(bindings[body][group][index]))
                    # Source-labelled limbs/gi remain in front for every skin tone.
                    p=np.asarray(layer).copy();p[PAD:][foreground(bindings[body][group][index])]=0
                    layer=Image.fromarray(p);bbox=layer.getbbox();assert bbox
                    assert bbox[2]-bbox[0]<=64 and bbox[3]-bbox[1]<=64
                    sx=count%14*64;sy=count//14*64;atlas.paste(layer.crop(bbox),(sx,sy))
                    entries[group].append({'x':bbox[0],'y':bbox[1],'w':bbox[2]-bbox[0],'h':bbox[3]-bbox[1],'sx':sx,'sy':sy,'sealed_texels':sealed})
                    from hair_palette import recolor
                    canvas=Image.new('RGBA',layer.size);canvas.paste(frame,(0,PAD));canvas.alpha_composite(recolor(layer,'castanho_escuro'))
                    cx,cy=fit['center'];crop=canvas.crop((round(cx)-28,round(cy)+PAD-28,round(cx)+28,round(cy)+PAD+32)).resize((112,120),Image.Resampling.NEAREST)
                    rx=count%14*120;ry=count//14*150;review.paste(crop,(rx,ry+20),crop);draw.text((rx+2,ry+3),f'{group}:{index+1}',fill='white');count+=1
            path=OUT/(style+'-'+body+'.png');atlas.save(path)
            result['styles'][style][body]={'path':path.relative_to(ROOT).as_posix(),'groups':entries}
            review.save(DOC/(style+'-'+body+'-all-poses.png'));print(style,body,count,flush=True)
    (ROOT/'assets/native-hair-poses.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
    (DOC/'native-pose-registration.json').write_text(json.dumps(fits,separators=(',',':'))+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--reuse-registration',action='store_true',help='Reuse reviewed skull fits when only authoring material extraction changed')
    main(parser.parse_args().reuse_registration)
