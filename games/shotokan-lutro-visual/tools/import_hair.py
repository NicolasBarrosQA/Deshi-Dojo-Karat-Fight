"""Extract hair material from authored cyan registration heads/green key sheets."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
from character_registry import write

ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'assets/source/hair-v1'
VIEWS=['front','three_quarter','profile','rear_three_quarter','rear','top']
STYLES=[('curto_classico','01-curto-classico','Curto clássico'),('medio_ondulado','02-medio-ondulado','Médio ondulado'),('crespo_curto','03-crespo-curto','Crespo curto')]
# Authored anatomical scalp centres and diameters in the registration cells.
REGISTRATION=[([256,270],340,380),([260,270],340,380),([253,270],340,380),([265,235],340,340),([256,230],340,340),([256,230],340,340)]

def main():
    result={'version':2,'styles':{}}
    for ident,name,label in STYLES:
        source=Image.open(SOURCE/(name+'-views.png')).convert('RGBA');cw=source.width//3;ch=source.height//2;views={}
        for i,view in enumerate(VIEWS):
            cell=source.crop((i%3*cw,i//3*ch,(i%3+1)*cw,(i//3+1)*ch));p=np.asarray(cell).copy();r,g,b,a=[p[:,:,c].astype(float) for c in range(4)]
            material=(a>0)&(r>g*1.08)&(g>b*1.03)&(r-b>9)
            grow=np.asarray(Image.fromarray((material*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)))>0
            ink=(np.maximum.reduce([r,g,b])<80)&(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])<38)
            visible=material|(grow&ink);p[:,:,3]=visible*255;p[~visible]=0
            image=Image.fromarray(p);image.save(SOURCE/(ident+'-'+view+'.png'))
            pivot,width,height=REGISTRATION[i];scale=cw/512
            views[view]={'path':'assets/source/hair-v1/'+ident+'-'+view+'.png','center':[v*scale for v in pivot],'width':width*scale,'height':height*scale}
        result['styles'][ident]={'label':label,'views':views}
    write(ROOT/'assets/hair-assets.json',result)

if __name__=='__main__':main()
