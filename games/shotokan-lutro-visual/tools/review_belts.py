"""Mechanical native-pixel annotation board; does not modify sprite artwork."""
import argparse,json
from PIL import Image,ImageDraw
from import_characters import HERE,W,H,binary
from character_masks import belt_mask

def board(body,start,count,plain=False):
    atlas=Image.open(HERE/'docs'/f'character-{body}-atlas.png').convert('RGBA')
    masks=json.loads((HERE/'assets/character-masks.json').read_text())[body]
    cloth_path=HERE/'assets'/f'character-belt-{body}-mask.png'
    cloth_atlas=Image.open(cloth_path).convert('L') if cloth_path.exists() else None
    cols=min(4,count);rows=(count+cols-1)//cols;cw=336;ch=324
    out=Image.new('RGB',(cols*cw,rows*ch),(220,222,224));d=ImageDraw.Draw(out)
    for n in range(count):
        i=start+n-1;x=n%cols*cw;y=n//cols*ch
        frame=binary(atlas.crop((i%4*W,i//4*H,(i%4+1)*W,(i//4+1)*H)))
        mask=cloth_atlas.crop((i%4*W,i//4*H,(i%4+1)*W,(i//4+1)*H)) if cloth_atlas else belt_mask(frame)
        for yy in range(H):
            for xx in range(W):
                if not plain and mask.getpixel((xx,yy)):frame.putpixel((xx,yy),(230,160,0,255))
        # Central crop still includes extended belt ends; 2x nearest zoom.
        crop=frame.crop((32,0,200,H)).resize((336,288),Image.Resampling.NEAREST)
        out.paste(crop,(x,y+24),crop)
        d.text((x+4,y+4),f'{body} pose {i+1}',fill='black')
        for gx in range(40,200,10):
            xx=x+(gx-32)*2;d.line((xx,y+24,xx,y+312),fill=(175,175,175));d.text((xx,y+313),str(gx),fill='black')
        for gy in range(10,144,10):d.text((x,y+24+gy*2),str(gy),fill='red')
    path=HERE/'docs'/f'belt-review-{body}-{start:02d}{"-plain" if plain else ""}.png';out.save(path);print(path)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('body');p.add_argument('start',type=int);p.add_argument('--count',type=int,default=16)
    p.add_argument('--plain',action='store_true')
    a=p.parse_args();board(a.body,a.start,a.count,a.plain)
