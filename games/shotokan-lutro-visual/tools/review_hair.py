"""Review baked hair on every approved pose, including scalp and floor edges."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw
from prepare_hair_bindings import animations
from hair_art import apply,read,PAD

ROOT=Path(__file__).resolve().parents[1];DOCS=ROOT/'docs/hair'

def main():
    config=json.loads((ROOT/'assets/characters.json').read_text());bindings=read('hair-bindings.json');allposes=animations()
    for style in ('curto_classico','medio_ondulado','crespo_curto'):
        overview=Image.new('RGB',(448*6,340*6),'#263c49');draw=ImageDraw.Draw(overview)
        selected=[('base',0),('base',8),('base',61),('ceremony',2),('knockdown',5),('hand_touch',4)]
        for row,body in enumerate(config['body_order']):
            student={'body':body,'hair':style,'appearance':{'hair_color':'branco' if row%2 else 'original'}};crops=[]
            for group,frames in allposes[body].items():
                for i,frame in enumerate(frames):
                    result=apply(frame,student,group,i);cx,cy=bindings[body][group][i]['center']
                    crop=result.crop((max(0,int(cx)-30),max(0,int(cy)-30+PAD),min(224,int(cx)+30),min(144+PAD,int(cy)+35+PAD)))
                    crops.append((f'{group}:{i+1}',crop))
            sheet=Image.new('RGB',(120*14,155*math.ceil(len(crops)/14)),'#344651');d=ImageDraw.Draw(sheet)
            for i,(key,crop) in enumerate(crops):
                x=i%14*120;y=i//14*155;crop=crop.resize((crop.width*2,crop.height*2),Image.Resampling.NEAREST);sheet.paste(crop,(x,y+20),crop);d.text((x+2,y+3),key,fill='white')
            sheet.save(DOCS/(body+'-'+style+'-all-heads.png'))
            for col,(group,i) in enumerate(selected):
                frame=apply(allposes[body][group][i],student,group,i).resize((448,(144+PAD)*2),Image.Resampling.NEAREST)
                overview.paste(frame,(col*448,row*340+20),frame);draw.text((col*448+6,row*340+4),body+' / '+group+':'+str(i+1),fill='white')
        overview.save(DOCS/(style+'-fit-review.png'));print(style,flush=True)

if __name__=='__main__':main()
