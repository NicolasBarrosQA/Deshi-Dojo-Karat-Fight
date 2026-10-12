"""Coordinate-labelled inspection crops for belt-mask annotations."""
from PIL import Image,ImageDraw
from import_characters import HERE,W,H

def detail(body,pose,bounds):
    i=pose-1;atlas=Image.open(HERE/'docs'/f'character-{body}-atlas.png').convert('RGBA')
    frame=atlas.crop((i%4*W,i//4*H,(i%4+1)*W,(i//4+1)*H))
    x0,y0,x1,y1=bounds;scale=10
    out=Image.new('RGB',((x1-x0)*scale+40,(y1-y0)*scale+40),'#dddddd')
    im=frame.crop(bounds).resize(((x1-x0)*scale,(y1-y0)*scale),Image.Resampling.NEAREST);out.paste(im,(30,30),im)
    d=ImageDraw.Draw(out)
    for x in range(x0,x1,5):
        xx=30+(x-x0)*scale;d.line((xx,30,xx,out.height-10),fill='#999999');d.text((xx,10),str(x),fill='black')
    for y in range(y0,y1,5):
        yy=30+(y-y0)*scale;d.line((30,yy,out.width-10,yy),fill='#999999');d.text((2,yy),str(y),fill='black')
    out.save(HERE/'docs'/f'belt-detail-{body}-{pose:02d}.png')

if __name__=='__main__':
    for b,p,r in [('adult',79,(100,40,160,100)),('teen',79,(100,50,155,110)),('child',79,(95,70,145,115)),('adult',54,(85,45,130,85)),('child',72,(100,95,140,125))]:detail(b,p,r)
