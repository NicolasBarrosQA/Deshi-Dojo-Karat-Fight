"""Authored greeting: mirror/material protection and contact for mixed heights."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps,ImageChops,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from skin_palette import PALETTES,apply_skin_palette,skin_coverage
from compile_character import transform
m=json.loads((ROOT/'assets/hand-touch-assets.json').read_text());assert len(m)==6
def frames(part,side='right'):
    atlas=Image.open(ROOT/'src/assets'/(part[side]+'.png')).convert('RGBA');result=[]
    assert set(atlas.getchannel('A').tobytes())<={0,255}
    for f in part['frames']:
        im=Image.new('RGBA',(224,144));im.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'] if side=='right' else 224-f['x']-f['w'],f['y']));result.append(im)
    return result
variants={};poses=tones=belts=0
for body,a in m.items():
    right=frames(a['body']);assert len(right)==9
    for im,other in zip(right,frames(a['body'],'left')):assert ImageOps.mirror(im).tobytes()==other.tobytes()
    for key,part in a['belts'].items():
        for i,(im,cloth,other) in enumerate(zip(right,frames(part),frames(part,'left'))):
            assert ImageOps.mirror(cloth).tobytes()==other.tobytes()
            assert not ImageChops.multiply(im.getchannel('A'),cloth.getchannel('A')).getbbox()
            assert list(Image.alpha_composite(im,cloth).getbbox())==a['bounds'][i] and a['bounds'][i][3]==143
            belts+=1
    for im in right:
        before=np.asarray(im);coverage=skin_coverage(im)
        for tone in PALETTES:
            after=np.asarray(apply_skin_palette(im,tone))
            assert np.array_equal(before[:,:,3],after[:,:,3])
            assert not np.any(np.any(before[:,:,:3]!=after[:,:,:3],axis=2)&(coverage==0));tones+=1
        poses+=1
    for height in (.94,1,1.04):
        for build in ('leve','medio','forte'):
            points=[];ap={'height':height,'build':build}
            for p in a['touch']:
                marker=Image.new('RGBA',(224,144));ImageDraw.Draw(marker).rectangle((p['x']-2,p['top'],p['x'],p['bottom']-1),fill='white')
                b=transform(marker,ap,a['bounds'][p['frame']-1]).getbbox();assert b
                transform(right[p['frame']-1],ap,a['bounds'][p['frame']-1])
                points.append({'x':b[2]-1,'top':b[1],'bottom':b[3]})
            variants[(body,height,build)]=points
cases=0
for first,x in variants.items():
    for second,y in variants.items():
        gap=min(max(p['top'],q['top'])-min(p['bottom'],q['bottom']) for p in x for q in y)
        assert gap<=1,(first,second,'contact heights do not meet',gap);cases+=1
report={'poses':poses,'belt_combinations':belts,'skin_combinations':tones,'mixed_body_height_build_contact_cases':cases,'mirror_alpha_and_materials':True}
(ROOT/'docs/hand-touch/asset-tests.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',json.dumps(report))
