"""Pose-attached authored hair; material and placement are baked, not runtime work."""
import json,math
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from hair_palette import recolor

ROOT=Path(__file__).resolve().parents[1];PAD=24

@lru_cache(maxsize=16)
def _read(path,stamp):return json.loads(Path(path).read_text(encoding='utf8'))

def read(name):
    p=ROOT/'assets'/name
    return _read(str(p),p.stat().st_mtime_ns) if p.exists() else {}

def styles():return read('hair-assets.json').get('styles',{})

def sources(student):
    style=styles().get(student.get('hair'))
    if not style:return []
    return [Path(__file__),ROOT/'tools/hair_palette.py',ROOT/'assets/hair-assets.json',ROOT/'assets/hair-bindings.json',*(ROOT/v['path'] for v in style['views'].values())]

@lru_cache(maxsize=512)
def _layer(path,stamp,width,color):
    with Image.open(path) as im:result=recolor(im.convert('RGBA'),color)
    result.thumbnail((round(result.width*width),round(result.height*width)),Image.Resampling.LANCZOS)
    # The game uses binary coverage; remove resampling fringes without tinting skin.
    p=np.asarray(result).copy();p[:,:,3]=(p[:,:,3]>=128)*255;p[p[:,:,3]==0]=0
    return Image.fromarray(p)

def overlay(student,group,index):
    style=styles().get(student.get('hair'))
    if not style:return None
    binding=read('hair-bindings.json')[student['body']][group][index]
    view=style['views'][binding['view']];path=ROOT/view['path'];scale=binding['width']/view['width']
    layer=_layer(str(path),path.stat().st_mtime_ns,scale,student['appearance']['hair_color']).copy()
    cx,cy=[v*scale for v in view['center']];w,h=layer.size
    if binding.get('mirror'):layer=ImageOps.mirror(layer);cx=w-1-cx
    angle=binding.get('angle',0)
    if angle:
        layer=layer.rotate(angle,Image.Resampling.NEAREST,expand=True)
        a=math.radians(angle);dx=cx-w/2;dy=cy-h/2
        cx=math.cos(a)*dx+math.sin(a)*dy+layer.width/2
        cy=-math.sin(a)*dx+math.cos(a)*dy+layer.height/2
    x=round(binding['center'][0]-cx);y=round(binding['center'][1]-cy)
    bounds=layer.getbbox()
    if bounds and (x+bounds[0]<0 or x+bounds[2]>224 or y+bounds[1]<-PAD or y+bounds[3]>144):
        raise ValueError(f'Cabelo recortado: {student["body"]}/{group}/{index+1}: {x,y,bounds}')
    result=Image.new('RGBA',(224,144+PAD));result.paste(layer,(x,y+PAD));result.info['logical_origin_y']=-PAD
    return result

def apply(frame,student,group,index):
    hair=overlay(student,group,index)
    if hair is None:return frame
    result=Image.new('RGBA',hair.size);result.paste(frame,(0,PAD));result.alpha_composite(hair)
    # Sleeves and hands that cross the scalp remain in front. The original bald
    # head material is preserved everywhere except the authored hair coverage.
    binding=read('hair-bindings.json')[student['body']][group][index]
    p=np.asarray(frame);rgb=p[:,:,:3].astype(float);r,g,b=[rgb[:,:,i] for i in range(3)]
    white=(p[:,:,3]>0)&(np.minimum.reduce([r,g,b])>135)&(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])<70)
    protect=white.copy()
    for y,start,end in binding.get('foreground_runs',[]):protect[y,start:end]=p[y,start:end,3]>0
    for rect in binding.get('occlusion',[]):protect[rect[1]:rect[3],rect[0]:rect[2]]=p[rect[1]:rect[3],rect[0]:rect[2],3]>0
    pixels=np.asarray(result).copy();pixels[PAD:PAD+144][protect]=p[protect]
    result=Image.fromarray(pixels);result.info['logical_origin_y']=-PAD
    return result

def logical_bounds(frame):
    b=frame.getbbox() or (0,0,1,1);dy=frame.info.get('logical_origin_y',0)
    return [b[0],b[1]+dy,b[2],b[3]+dy]
