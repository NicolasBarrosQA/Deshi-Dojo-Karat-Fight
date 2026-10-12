"""Only the descent placement changes; mirrored pixels and source import agree."""
import json,copy,sys,zipfile
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from avatar_set_import import align_jump_transition,jump_cap_center
read=lambda p:json.loads(p.read_text(encoding='utf8'))
result=read(ROOT/'docs/avatar-set-v3/jump-anchor-correction.json');new=read(ROOT/'assets/character-assets.json');masks=read(ROOT/'assets/character-masks.json')
with zipfile.ZipFile(result['backup']) as z:
    old=json.loads(z.read('assets/character-assets.json'));oldmasks=json.loads(z.read('assets/character-masks.json'))
def unpack(part,index):
    f=part['frames'][index];atlas=Image.open(ROOT/'src/assets'/(part['right']+'.png')).convert('RGBA')
    frame=Image.new('RGBA',(224,144));frame.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']));return frame
for body,b in new.items():
    dx=next(c['shift_x'] for c in result['changes'] if c['body']==body)
    for layer,variants in old[body]['parts'].items():
        for key,p in variants.items():
            expected=copy.deepcopy(p);f=expected['frames'][62]
            if f['w']>1 or f['h']>1:f['x']+=dx
            assert expected==b['parts'][layer][key],(body,layer,key,'Unrelated pose or raster changed')
    for index,(before,after) in enumerate(zip(old[body]['bounds'],b['bounds'])):
        expected=before.copy()
        if index==62:expected[0]+=dx;expected[2]+=dx
        assert after==expected
    assert abs(jump_cap_center(unpack(b['parts']['body']['default'],61))-jump_cap_center(unpack(b['parts']['body']['default'],62)))<=.5,(body,'Cranial cap shifted')
    frames=[Image.new('RGBA',(224,144)) for _ in range(9)];cloth=[Image.new('L',(224,144)) for _ in range(9)];entries=[{} for _ in range(9)]
    for i,pose in [(7,61),(8,62)]:
        frames[i]=unpack(old[body]['parts']['body']['default'],pose)
        cloth[i]=unpack(old[body]['parts']['belt']['branca'],pose).getchannel('A')
        entries[i]={'head':oldmasks[body][str(pose+1)]['head'].copy(),'belt':oldmasks[body][str(pose+1)]['belt'].copy(),'bounds':old[body]['bounds'][pose].copy()}
    assert align_jump_transition(frames,cloth,entries)==dx
    assert frames[8].tobytes()==unpack(b['parts']['body']['default'],62).tobytes(),(body,'Source import differs from installed fix')
print('PASS six descent anchors, unchanged other poses/pixels/scale, source-import parity')
