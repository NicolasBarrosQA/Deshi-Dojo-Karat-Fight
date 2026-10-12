"""Mechanical ownership extraction; never cuts cross-cell fists or feet."""
from array import array
from collections import deque
from PIL import Image

def figures(sheet,cols,rows,strict=True):
    width,height=sheet.size
    alpha=sheet.getchannel('A').point(lambda v:255 if v>=128 else 0).tobytes()
    labels=array('i',[0])*(width*height);components=[]
    for seed,value in enumerate(alpha):
        if not value or labels[seed]:continue
        tag=len(components)+1;labels[seed]=tag;queue=deque([seed]);pixels=[];sx=sy=0
        while queue:
            pos=queue.popleft();pixels.append(pos);sx+=pos%width;sy+=pos//width
            x,y=pos%width,pos//width
            for nxt in (pos-1 if x else -1,pos+1 if x+1<width else -1,
                        pos-width if y else -1,pos+width if y+1<height else -1):
                if nxt>=0 and alpha[nxt] and not labels[nxt]:
                    labels[nxt]=tag;queue.append(nxt)
        components.append((pixels,sx/len(pixels),sy/len(pixels)))
    bodies=sorted(components,key=lambda c:len(c[0]),reverse=True)[:rows*cols]
    assert len(bodies)==rows*cols and all(len(c[0])>1000 for c in bodies),'Missing complete figure'
    bodies.sort(key=lambda c:c[2]);ordered=[]
    for row in range(rows):ordered.extend(sorted(bodies[row*cols:(row+1)*cols],key=lambda c:c[1]))
    cells=[]
    for i,(pixels,cx,cy) in enumerate(ordered):
        col,row=i%cols,i//cols
        if strict:assert round(col*width/cols)<=cx<round((col+1)*width/cols),(i,'column ownership')
        if strict:assert round(row*height/rows)<=cy<round((row+1)*height/rows),(i,'row ownership')
        mask=bytearray(width*height)
        for pos in pixels:mask[pos]=255
        layer=sheet.copy();layer.putalpha(Image.frombytes('L',(width,height),bytes(mask)))
        cells.append(layer.crop(layer.getbbox()))
    return cells
