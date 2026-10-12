"""Measure the cranial oval rather than a skin component joined to a forearm."""
import math
import numpy as np
from PIL import Image,ImageFilter

def skin_mask(frame):
    p=np.asarray(frame).astype(float);r,g,b,a=[p[:,:,i] for i in range(4)]
    return (a>0)&(r>55)&(r>g*1.055)&(g>b*1.015)&(r-b>16)

def distance(mask):
    # Chamfer distance needs only NumPy and has no new runtime dependency.
    d=np.where(mask,1000.,0.)
    for _ in range(18):
        p=np.pad(d,1,constant_values=0)
        neighbors=[d]
        for dy,dx,cost in ((0,1,1),(0,-1,1),(1,0,1),(-1,0,1),(1,1,math.sqrt(2)),(1,-1,math.sqrt(2)),(-1,1,math.sqrt(2)),(-1,-1,math.sqrt(2))):
            neighbors.append(p[1+dy:1+dy+d.shape[0],1+dx:1+dx+d.shape[1]]+cost)
        d=np.minimum.reduce(neighbors)
    return d

def measure(frame,expected_angle=0):
    mask=skin_mask(frame);dist=distance(mask);maximum=float(dist.max())
    # Feet/hands have a smaller interior radius than the cranium. Prefer the
    # centre of the plateau to avoid one-pixel sampling changes between poses.
    yy,xx=np.where(dist>=maximum-.35);cx=float(np.mean(xx));cy=float(np.mean(yy))
    if len(xx)>30 or xx.max()-xx.min()>25 or yy.max()-yy.min()>25:
        y,x=np.unravel_index(np.argmax(dist),dist.shape);cx=float(x);cy=float(y)
    rows,cols=np.indices(mask.shape);radius=maximum+3.0
    region=mask&((cols-cx)**2+(rows-cy)**2<radius**2)
    py,px=np.where(region)
    covariance=np.cov(np.stack([px-cx,py-cy]));values,vectors=np.linalg.eigh(covariance);v=vectors[:,np.argmax(values)]
    if v[1]>0:v=-v
    measured=math.degrees(math.atan2(-v[0],-v[1]))
    while measured-expected_angle>90:measured-=180
    while measured-expected_angle<-90:measured+=180
    confidence=float(max(values)/max(.001,min(values)))
    angle=measured if confidence>1.35 and abs(measured-expected_angle)<30 else expected_angle
    a=math.radians(angle);dx=cols-cx;dy=rows-cy
    localx=np.cos(a)*dx-np.sin(a)*dy;localy=np.sin(a)*dx+np.cos(a)*dy
    # Grow out from the inscribed circle only to the authored skull boundary.
    # Neck, ears and touching arms cannot enlarge the oval past these limits.
    rx=maximum;ry=rx*1.05
    oval=(localx/rx)**2+(localy/ry)**2<=1.05
    # Source-only semantic foreground survives every subsequent skin palette.
    p=np.asarray(frame);rgb=p[:,:,:3].astype(float);r,g,b=[rgb[:,:,i] for i in range(3)]
    white=(p[:,:,3]>0)&(np.minimum.reduce([r,g,b])>130)&(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])<75)
    # The oval measures the cranium; it is not a cutout mask. Using it as one
    # would restore bald scalp pixels through the hair along its perimeter.
    head_envelope=(localx/(rx*1.3))**2+(localy/(ry*1.35))**2<=1.05
    outside=mask&~head_envelope
    near_scalp=(np.abs(cols-cx)<rx*2.6)&(np.abs(rows-cy)<ry*2.6)
    # A raised hand can touch the scalp and become the very same skin component.
    # Its one-pixel contact edge stays in front rather than becoming hair.
    if np.count_nonzero(outside&near_scalp&(localy<-ry-.5))>=6:
        yy,xx=np.where(outside&near_scalp&(localy<0))
        points=np.stack([xx,yy],axis=1).astype(float);middle=points.mean(axis=0)
        values,vectors=np.linalg.eigh(np.cov(points.T));axis=vectors[:,np.argmax(values)];normal=np.array([-axis[1],axis[0]])
        along=(points-middle)@axis;across=(points-middle)@normal
        if max(values)/max(.001,min(values))>3:
            thickness=float(np.percentile(np.abs(across),95))+.8
            projection=(cols-middle[0])*axis[0]+(rows-middle[1])*axis[1]
            cross=(cols-middle[0])*normal[0]+(rows-middle[1])*normal[1]
            arm=(np.abs(cross)<thickness)&(projection>=along.min()-.8)&(projection<=along.max()+.8)
            outside|=arm&mask&(localy<0)
    protect=white|outside
    near=np.asarray(Image.fromarray((protect*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)))>0
    dark=(p[:,:,3]>0)&(np.maximum.reduce([r,g,b])<100)
    protect|=near&dark
    protect&=near_scalp
    return {'center':[round(cx,2),round(cy,2)],'width':round(rx*2,2),'height':round(ry*2,2),'angle':round(angle,2),'inscribed_radius':round(maximum,2)},protect

def runs(mask):
    result=[]
    for y,row in enumerate(mask):
        padded=np.pad(row.astype('int8'),1);edges=np.where(np.diff(padded)!=0)[0]
        for start,end in zip(edges[::2],edges[1::2]):result.append([int(y),int(start),int(end)])
    return result

def beard_foreground(frame,binding):
    """Source-labelled clothes/limbs, with a jaw-sized opening for facial hair."""
    p=np.asarray(frame);rgb=p[:,:,:3].astype(float);r,g,b=[rgb[:,:,i] for i in range(3)]
    rows,cols=np.indices(p.shape[:2]);cx,cy=binding['center'];rx=binding['width']/2;ry=binding['height']/2
    a=math.radians(binding.get('angle',0));dx=cols-cx;dy=rows-cy
    x=np.cos(a)*dx-np.sin(a)*dy;y=np.sin(a)*dx+np.cos(a)*dy
    face=(np.abs(x)<rx*1.4)&(y>-ry*.4)&(y<ry*1.8)
    white=(p[:,:,3]>0)&(np.minimum.reduce([r,g,b])>130)&(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])<75)
    protect=white|(skin_mask(frame)&~face)
    near=np.asarray(Image.fromarray((white*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)))>0
    protect|=near&(p[:,:,3]>0)&(np.maximum.reduce([r,g,b])<100)
    for px,py in binding.get('foreground_points',[]):protect[py,px]=True
    protect&=(np.abs(x)<rx*2.6)&(np.abs(y)<ry*2.6)
    return protect
