"""Authored body contracts: complete poses, binary alpha, exact mirror and belts."""
import json,sys,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageChops
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from character_registry import read,validate,DEFAULT,catalog
from compile_character import transform
from import_female_bodies import original_part as packed
OUT=ROOT/'docs/female-bodies';OUT.mkdir(parents=True,exist_ok=True)
config=read(ROOT/'assets/characters.json');base=read(ROOT/'assets/character-assets.json');special=read(ROOT/'assets/special-assets.json')
existing={} # All six old bodies intentionally replaced by approved neutral 2D art.
assert all(b.get('revision')=='neutral-2d-v3' for b in base.values())
allframes={};checks=0;belt_checks=0
def inspect(body,group,parts):
    global checks,belt_checks
    full=[]
    n=92 if group=='base' else 9
    for part in parts:
        right=Image.open(ROOT/'src/assets'/(part['right']+'.png')).convert('RGBA');left=Image.open(ROOT/'src/assets'/(part['left']+'.png')).convert('RGBA')
        assert len(part['frames'])==n
        for r in part['frames']:
            box=(r['sx'],r['sy'],r['sx']+r['w'],r['sy']+r['h']);a=right.crop(box);b=left.crop(box)
            assert set(a.getchannel('A').tobytes())<={0,255};assert ImageOps.mirror(a).tobytes()==b.tobytes();checks+=1
    for i in range(n):
        f=Image.new('RGBA',(224,144))
        for part in parts:f.alpha_composite(packed(part,i))
        box=f.getbbox();assert box and 0<=box[0]<box[2]<=224 and 0<=box[1]<box[3]<=144
        f.save(OUT/f'{body}-{group}-{i+1:02d}.png');full.append(f)
        for height in (.94,1,1.04):
            for build in ('leve','medio','forte'):transform(f,{**DEFAULT,'height':height,'build':build},box)
    return full
for age in ('adult','teen','child'):
    body=age+'_female';assert body in config['body_order']
    assert validate({'id':'test-female','name':'Teste','body':body,'belt':'branca'},config,base)['body']==body
    allframes[body]={}
    parts=[base[body]['parts'][k]['default'] for k in ('body','face','hair','foreground')]+[base[body]['parts']['belt']['preta']]
    allframes[body]['base']=inspect(body,'base',parts)
    assert hashlib.sha256(packed(base[body]['parts']['body']['default'],0).tobytes()).digest()!=hashlib.sha256(packed(base[age]['parts']['body']['default'],0).tobytes()).digest()
    for group,s in special[body].items():allframes[body][group]=inspect(body,group,[s['body'],s['belts']['preta']])
    for group in allframes[body]:
        rec=base[body]['parts']['belt'] if group=='base' else special[body][group]['belts']
        for i in range(len(allframes[body][group])):
            alpha=packed(rec['preta'],i).getchannel('A')
            for belt,part in rec.items():assert packed(part,i).getchannel('A').tobytes()==alpha.tobytes();belt_checks+=1
for group in allframes['adult_female']:
    count=len(allframes['adult_female'][group])
    for start in range(0,count,9):
        sheet=Image.new('RGBA',(2016,432))
        for row,age in enumerate(('adult','teen','child')):
            for col,f in enumerate(allframes[age+'_female'][group][start:start+9]):sheet.paste(f,(col*224,row*144))
        sheet.resize((4032,864),Image.Resampling.NEAREST).save(OUT/f'{group}-{start+1:02d}.png')
write={'poses':492,'layer_mirror_binary_checks':checks,'belt_alpha_checks':belt_checks,'existing_asset_hashes':len(existing),'native_hardware_tested':False}
(OUT/'tests.json').write_text(json.dumps(write,indent=2)+'\n');print(json.dumps(write))
