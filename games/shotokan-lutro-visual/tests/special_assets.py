"""All authored cells, mirror geometry, alpha and cloth-only recoloring."""
import json,sys
from pathlib import Path
from PIL import Image,ImageOps,ImageChops
HERE=Path(__file__).resolve().parents[1]
manifest=json.loads((HERE/'assets/special-assets.json').read_text());cache={};count=0
def unpack(part,side):
 name=part[side]
 if name not in cache:cache[name]=Image.open(HERE/'src/assets'/(name+'.png')).convert('RGBA')
 atlas=cache[name];assert atlas.size==(part['width'],part['height'])
 assert set(atlas.getchannel('A').tobytes())<={0,255}
 result=[]
 for f in part['frames']:
  assert 0<=f['sx']<=part['width']-f['w'] and 0<=f['sy']<=part['height']-f['h']
  im=Image.new('RGBA',(224,144));im.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'] if side=='right' else 224-f['x']-f['w'],f['y']));result.append(im)
 assert len(result)==9
 return result
for body,groups in manifest.items():
 assert len(groups)==8,(body,'missing animation')
 for group,a in groups.items():
  right=unpack(a['body'],'right');left=unpack(a['body'],'left');cloth=unpack(a['belts']['preta'],'right')
  for i,(r,l,b) in enumerate(zip(right,left,cloth)):
   assert l.tobytes()==ImageOps.mirror(r).tobytes(),(body,group,i,'body mirror')
   assert not ImageChops.multiply(r.getchannel('A'),b.getchannel('A')).getbbox(),(body,group,i,'cloth overlap')
   original=Image.alpha_composite(r,b);assert list(original.getbbox())==a['bounds'][i]
   assert original.getbbox()[3]==143,(body,group,i,'floor anchor')
   count+=1
  for color,part in a['belts'].items():
   colored=unpack(part,'right');mirrored=unpack(part,'left')
   for i,(r,b,c,l) in enumerate(zip(right,cloth,colored,mirrored)):
    assert c.getchannel('A').tobytes()==b.getchannel('A').tobytes(),(body,group,i,color,'cloth shape')
    assert l.tobytes()==ImageOps.mirror(c).tobytes(),(body,group,i,color,'belt mirror')
    original=Image.alpha_composite(r,b);new=Image.alpha_composite(r,c)
    diff=ImageChops.difference(original.convert('RGB'),new.convert('RGB'));channels=diff.split();changed=ImageChops.lighter(ImageChops.lighter(*channels[:2]),channels[2]).point(lambda x:255 if x else 0)
    assert not ImageChops.subtract(changed,b.getchannel('A')).getbbox(),(body,group,i,color,'escaped cloth')
assert count==9*8*len(manifest)
result={'poses':count,'groups':8,'bodies':len(manifest),'checks':['9 cells per animation','binary alpha','exact mirrors','ground anchor','cloth silhouette retained across eight belts','no recoloring outside cloth'],'anatomy':'Separate visual review in docs/avatar-set-v3; this automated test does not judge anatomy.'}
(HERE/'docs/special-assets-results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',count,'special poses and',count*8,'belt variants')
