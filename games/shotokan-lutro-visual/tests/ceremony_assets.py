"""Real authored presentation atlas: anatomy scale, feet, palette and endpoint."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps,ImageChops
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from skin_palette import PALETTES,apply_skin_palette,skin_coverage
from avatar_set_import import groups,area,box
manifest=json.loads((ROOT/'assets/ceremony-assets.json').read_text())
base=json.loads((ROOT/'assets/character-assets.json').read_text())
def unpack(part,side='right'):
    atlas=Image.open(ROOT/'src/assets'/(part[side]+'.png')).convert('RGBA');result=[]
    assert atlas.size==(part['width'],part['height']) and set(atlas.getchannel('A').tobytes())<={0,255}
    for f in part['frames']:
        im=Image.new('RGBA',(224,144));im.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'] if side=='right' else 224-f['x']-f['w'],f['y']));result.append(im)
    return result
assert len(manifest)==6
for body,a in manifest.items():
    frames=unpack(a['body']);assert len(frames)==9
    guard=unpack(base[body]['parts']['body']['default'])[0]
    assert frames[7].tobytes()==guard.tobytes()
    for im,mirror in zip(frames,unpack(a['body'],'left')):assert ImageOps.mirror(im).tobytes()==mirror.tobytes()
    for belt,part in a['belts'].items():
        belts=unpack(part);assert belts[7].tobytes()==unpack(base[body]['parts']['belt'][belt])[0].tobytes()
        for index,(im,cloth,opposite) in enumerate(zip(frames,belts,unpack(part,'left'))):
            assert ImageOps.mirror(cloth).tobytes()==opposite.tobytes()
            assert not ImageChops.multiply(im.getchannel('A'),cloth.getchannel('A')).getbbox()
            assert list(Image.alpha_composite(im,cloth).getbbox())==a['bounds'][index]
            assert a['bounds'][index][3]==143
    for im in frames:
        before=np.asarray(im);coverage=skin_coverage(im)
        for tone in PALETTES:
            after=np.asarray(apply_skin_palette(im,tone))
            assert np.array_equal(before[:,:,3],after[:,:,3])
            assert not np.any(np.any(before[:,:,:3]!=after[:,:,:3],axis=2)&(coverage==0))
    # Same skull diameter prevents the old shrinking-during-animation bug.
    white=unpack(a['belts']['branca'])
    def head_width(im):
        p=np.asarray(im).astype(np.int16);r,g,b,a=[p[:,:,i] for i in range(4)]
        parts=[c for c in groups((a>0)&(r>g*1.10)&(g>b*1.06)&(r-b>24)&(r>55)) if area(c)>25 and box(c)[1]<100]
        c=min(parts,key=lambda c:box(c)[1]);l,t,rr,bb=box(c)
        return max(e-s for y,s,e in c if y<t+(bb-t)*.45)
    widths=[head_width(Image.alpha_composite(im,b)) for im,b in zip(frames,white)]
    assert max(widths)-min(widths)<=4,(body,widths)
print('PASS 54 presentation poses, 432 belt combinations, 648 skin combinations, original guard endpoints and scale')
