"""Semantic masks and size landmarks from existing sprite pixels."""
from collections import deque
from PIL import Image,ImageFilter,ImageDraw

def components(mask):
    w,h=mask.size;remaining=set(i for i,v in enumerate(mask.tobytes()) if v);out=[]
    while remaining:
        seed=remaining.pop();q=deque([seed]);pixels=[seed]
        while q:
            i=q.popleft();x,y=i%w,i//w
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    xx,yy=x+dx,y+dy;j=yy*w+xx
                    if 0<=xx<w and 0<=yy<h and j in remaining:
                        remaining.remove(j);q.append(j);pixels.append(j)
        out.append(pixels)
    return sorted(out,key=len,reverse=True)

def hair_bounds(frame):
    b=frame.getbbox();w,h=frame.size;mask=Image.new('L',frame.size)
    for y in range(b[1],b[1]+round((b[3]-b[1])*.32)):
        for x in range(b[0],b[2]):
            r,g,bl,a=frame.getpixel((x,y))
            if a and max(r,g,bl)<95:mask.putpixel((x,y),255)
    groups=components(mask);assert groups,'missing hair landmark'
    pixels=groups[0]
    return (min(i%w for i in pixels),min(i//w for i in pixels),max(i%w for i in pixels)+1,max(i//w for i in pixels)+1)

def belt_mask(frame,override=None):
    w,h=frame.size;b=frame.getbbox();hair=hair_bounds(frame)
    dark=Image.new('L',frame.size)
    # Hair and bare limbs cannot seed the belt component.
    for y in range(hair[3]+4,min(h,b[3]-4)):
        for x in range(b[0],b[2]):
            r,g,bl,a=frame.getpixel((x,y))
            if a and max(r,g,bl)<105:dark.putpixel((x,y),255)
    core=dark.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    groups=components(core);assert groups,'missing belt component'
    # Thick black cloth survives opening; one-pixel gi contours do not.
    cx=(hair[0]+hair[2])/2
    selected=min(groups,key=lambda p:abs(sum(i%w for i in p)/len(p)-cx)*.35+abs(sum(i//w for i in p)/len(p)-(b[1]+(b[3]-b[1])*.56))-min(len(p),250)*.12)
    result=Image.new('L',frame.size)
    for i in selected:result.putpixel((i%w,i//w),255)
    # Recover dark cloth edges only adjacent to the thick cloth interior.
    expanded=result.filter(ImageFilter.MaxFilter(3))
    for y in range(h):
        for x in range(w):
            if expanded.getpixel((x,y)) and dark.getpixel((x,y)):result.putpixel((x,y),255)
    if override:
        if override.get('replace'):result=Image.new('L',frame.size)
        included=Image.new('L',frame.size);d=ImageDraw.Draw(included)
        for polygon in override.get('include',[]):d.polygon([tuple(p) for p in polygon],fill=255)
        excluded=Image.new('L',frame.size);d=ImageDraw.Draw(excluded)
        for polygon in override.get('exclude',[]):d.polygon([tuple(p) for p in polygon],fill=255)
        for y in range(h):
            for x in range(w):
                pixel=frame.getpixel((x,y))
                if included.getpixel((x,y)) and pixel[3] and max(pixel[:3])<125:result.putpixel((x,y),255)
                if excluded.getpixel((x,y)):result.putpixel((x,y),0)
    return result
