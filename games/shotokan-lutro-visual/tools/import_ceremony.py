"""Pack original 2D rei/yoi/kiba art with existing anatomy and belt isolation."""
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from avatar_set_import import figures,cranial_width,normalize,palettes,separate,BODIES
from compile_character import pack
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/source/ceremony'
OUT=ROOT/'src/assets'
DOCS=ROOT/'docs/ceremony';DOCS.mkdir(parents=True,exist_ok=True)
config=json.loads((ROOT/'assets/characters.json').read_text())
base=json.loads((ROOT/'assets/character-assets.json').read_text())
result={};report={}
def unpack(part,index):
    f=part['frames'][index];atlas=Image.open(OUT/(part['right']+'.png')).convert('RGBA')
    im=Image.new('RGBA',(224,144));im.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']));return im
for body,(_,height) in BODIES.items():
    path=SOURCE/(body+'.png')
    cells=figures(Image.open(path).convert('RGBA'))
    reference=figures(Image.open(ROOT/'assets/source/avatar-set-v3'/body/'base-01.png').convert('RGBA'))[0]
    target=cranial_width(reference)*height/reference.height
    frames=[];masks=[];entries=[]
    for index,cell in enumerate(cells):
        frame,mask,entry=normalize(cell,target/cranial_width(cell))
        frames.append(frame);masks.append(mask);entries.append(entry)
    # The endpoint is the approved in-game guard pixel-for-pixel.
    guard=unpack(base[body]['parts']['body']['default'],0)
    white=unpack(base[body]['parts']['belt']['branca'],0)
    frames[7]=Image.alpha_composite(guard,white);masks[7]=white.getchannel('A')
    # Planted feet do not drift while the torso bows, or when attention returns.
    def foot_center(im):
        yy,xx=np.nonzero(np.asarray(im.getchannel('A'))[137:143]);return float(np.median(xx))
    origin=foot_center(frames[0])
    for index in (1,2,3):
        dx=round(origin-foot_center(frames[index]))
        bounds=frames[index].getbbox()
        assert 0<=bounds[0]+dx<bounds[2]+dx<=224
        for images in (frames,masks):
            im=Image.new(images[index].mode,images[index].size);im.paste(images[index],(dx,0));images[index]=im
        entries[index]['planted_feet_shift_x']=dx
    rec={'body':pack(separate(frames,masks),'special-'+body+'-ceremony',OUT),
         'belts':palettes(frames,masks,'special-'+body+'-ceremony-belt',config,OUT),
         'bounds':[list(im.getbbox()) for im in frames]}
    for belt,part in list(rec['belts'].items()):
        values=[unpack(part,i) for i in range(9)]
        values[7]=unpack(base[body]['parts']['belt'][belt],0)
        rec['belts'][belt]=pack(values,'special-'+body+'-ceremony-belt-'+belt,OUT)
    result[body]=rec;report[body]={'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'poses':entries,'guard_endpoint_reused':True}
    page=Image.new('RGB',(224*3,165*3),(27,34,40));draw=ImageDraw.Draw(page)
    labels=['REI - ATENCAO','REI - INICIO','OSS - REVERENCIA','REI - RETORNO','YOI - TRANSICAO','YOI','ENTRADA NA GUARDA','KAMAE APROVADO','KIBA-DACHI']
    for i,frame in enumerate(frames):
        x=i%3*224;y=i//3*165;page.paste(frame,(x,y),frame);draw.text((x+8,y+147),labels[i],fill='white')
    page.save(DOCS/(body+'.png'))
    print('Imported',body,'9 authored poses',flush=True)
(ROOT/'assets/ceremony-assets.json').write_text(json.dumps(result,indent=2)+'\n')
(DOCS/'import-report.json').write_text(json.dumps(report,indent=2)+'\n')
