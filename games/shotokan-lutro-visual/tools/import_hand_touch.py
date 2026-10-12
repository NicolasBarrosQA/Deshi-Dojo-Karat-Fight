"""Import authored greeting poses and annotate knuckle contact, without deformation."""
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from avatar_set_import import figures,cranial_width,normalize,palettes,separate,BODIES,groups,area,box
from compile_character import pack
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'assets/source/hand-touch';OUT=ROOT/'src/assets'
DOCS=ROOT/'docs/hand-touch';DOCS.mkdir(parents=True,exist_ok=True)
config=json.loads((ROOT/'assets/characters.json').read_text());manifest={};reports={}
def contact(im):
    p=np.asarray(im).astype(np.int16);r,g,b,a=[p[:,:,i] for i in range(4)]
    parts=groups((a>0)&(r>g*1.055)&(g>b*1.015)&(r-b>16)&(r>55))
    head=min((p for p in parts if area(p)>20),key=lambda p:box(p)[1]);cutoff=box(head)[1]+8
    hand=max((p for p in parts if area(p)>8 and box(p)[1]>cutoff),key=lambda p:box(p)[2])
    right=box(hand)[2];ys=[y for y,s,e in hand if e>=right-2]
    return {'x':right-1,'top':min(ys),'bottom':max(ys)+1}
for body,(_,height) in BODIES.items():
    path=SOURCE/(body+'.png');cells=figures(Image.open(path).convert('RGBA'))
    corrections=SOURCE/'corrections.json'
    if corrections.exists():
        change=json.loads(corrections.read_text()).get(body)
        if change:
            fixed=figures(Image.open(SOURCE/change['source']).convert('RGBA'))
            for index in change['cells']:cells[index]=fixed[index]
    ref=figures(Image.open(ROOT/'assets/source/avatar-set-v3'/body/'base-01.png').convert('RGBA'))[0]
    target=cranial_width(ref)*height/ref.height
    frames=[];masks=[];entries=[]
    for cell in cells:
        frame,mask,entry=normalize(cell,target/cranial_width(cell));frames.append(frame);masks.append(mask);entries.append(entry)
    hands=[{'frame':i+1,**contact(frames[i])} for i in (4,5,6)]
    rec={'body':pack(separate(frames,masks),'special-'+body+'-hand-touch',OUT),
         'belts':palettes(frames,masks,'special-'+body+'-hand-touch-belt',config,OUT),
         'bounds':[list(f.getbbox()) for f in frames],'touch':hands}
    manifest[body]=rec;reports[body]={'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'contact':hands,'poses':entries}
    page=Image.new('RGB',(672,495),(27,34,40));draw=ImageDraw.Draw(page)
    labels=['ATENCAO','PASSO','APROXIMAR','OFERECER A MAO','TOQUE ALTO','TOQUE MEDIO','TOQUE BAIXO','RECOLHER','RETORNO']
    for i,f in enumerate(frames):
        x=i%3*224;y=i//3*165;page.paste(f,(x,y),f);draw.text((x+6,y+147),labels[i],fill='white')
    page.save(DOCS/(body+'.png'));print(body,hands,flush=True)
(ROOT/'assets/hand-touch-assets.json').write_text(json.dumps(manifest,indent=2)+'\n')
(DOCS/'import-report.json').write_text(json.dumps(reports,indent=2)+'\n')
