"""Publish only the two approved cuts; keep rejected legacy sources withdrawn."""
import json
from pathlib import Path
from PIL import Image
from prepare_hair_bindings import animations
from hair_art import apply,PAD
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'assets/hair-assets.json';data=json.loads(path.read_text())
for value in data['styles'].values():value['available']=False
for key,label,category in [('masculino_curto','Curto aprovado','masculino'),('feminino_chanel','Chanel aprovado','feminino')]:
    data['styles'][key]={'label':label,'category':category,'available':True,'views':{},'pose_layers':'native-hair-poses.json','revision':'native-skull-v2'}
data['version']=4;path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
poses=animations();thumbs=ROOT/'assets/source/hair-catalog-v1/thumbnails';thumbs.mkdir(exist_ok=True)
for style,body in [('masculino_curto','adult'),('feminino_chanel','adult_female')]:
    student={'body':body,'hair':style,'appearance':{'hair_color':'original'}}
    frame=apply(poses[body]['base'][0],student,'base',0)
    from hair_art import read
    cx,cy=read('hair-bindings.json')[body]['base'][0]['center']
    crop=frame.crop((int(cx)-24,int(cy)+PAD-24,int(cx)+24,int(cy)+PAD+24)).resize((96,96),Image.Resampling.NEAREST)
    crop.save(thumbs/(style+'.png'))
print('Two approved native cuts published; 23 legacy cuts remain withdrawn')
