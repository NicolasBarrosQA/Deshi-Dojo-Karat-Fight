"""Contact pages drawn from the same pose compositor as production export."""
import math
from pathlib import Path
from PIL import Image,ImageDraw
from hair_art import styles,beards,apply,read,PAD
from prepare_hair_bindings import animations

ROOT=Path(__file__).resolve().parents[1]
def main():
    poses=animations();out=ROOT/'docs/hair-catalog';out.mkdir(exist_ok=True)
    for kind,catalog in [('hair',styles()),('beard',beards())]:
        entries=list(catalog.items())
        for offset in range(0,len(entries),8):
            chosen=entries[offset:offset+8]
            for group,index,name in [('base',0,'guard'),('base',14,'raised-hand'),('knockdown',4,'floor')]:
                sheet=Image.new('RGB',(6*132,120*len(chosen)),'#233741');draw=ImageDraw.Draw(sheet)
                for row,(ident,entry) in enumerate(chosen):
                    draw.text((4,row*120+2),entry['label'],fill='#efc989')
                    for col,body in enumerate(poses):
                        student={'body':body,'hair':ident if kind=='hair' else 'default','beard':ident if kind=='beard' else 'default','appearance':{'hair_color':'original','beard_color':'original'}}
                        im=apply(poses[body][group][index],student,group,index);cx,cy=read('hair-bindings.json')[body][group][index]['center']
                        crop=im.crop((round(cx)-24,round(cy)+PAD-22,round(cx)+24,round(cy)+PAD+25)).resize((96,94),Image.Resampling.NEAREST)
                        x=col*132;y=row*120+20;sheet.paste(crop,(x,y),crop);draw.text((x,y+94),body,fill='white')
                sheet.save(out/(kind+'-'+name+'-'+str(offset//8+1)+'.png'))
    print('Review pages generated from production compositor')
if __name__=='__main__':main()
