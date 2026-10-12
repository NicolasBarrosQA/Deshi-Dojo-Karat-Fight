"""Audit every body/move/tone: material coverage, alpha, ink and shading."""
import sys,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from skin_palette import PALETTES,skin_coverage,apply_skin_palette,palette_lut
OUT=ROOT/'docs/skin-personalization';OUT.mkdir(parents=True,exist_ok=True)
def read(path):return json.loads(path.read_text(encoding='utf8'))
base=read(ROOT/'assets/character-assets.json');specials=read(ROOT/'assets/special-assets.json')
for key in PALETTES:
    if key=='original':continue
    lut=palette_lut(key);luma=lut@np.array([.2126,.7152,.0722]);assert np.all(np.diff(luma)>0),(key,'Collapsed shading')
    assert len(np.unique(np.rint(lut).astype(np.uint8),axis=0))>150,(key,'Posterized ramp')
fixture=Image.new('RGBA',(6,1));fixture.putdata([(240,241,247,255),(88,91,105,255),(20,15,14,255),(230,175,125,255),(170,30,150,0),(230,175,125,0)])
for key in PALETTES:
    after=apply_skin_palette(fixture,key)
    for x in [0,1,2,4,5]:assert after.getpixel((x,0))==fixture.getpixel((x,0)),(key,'Protected cloth/ink/transparent pixel')
poses=variants=changed=0
for body,b in base.items():
    groups={'basic':b['parts']['body']['default'],**{g:a['body'] for g,a in specials[body].items()}}
    for group,part in groups.items():
        atlas=Image.open(ROOT/'src/assets'/(part['right']+'.png')).convert('RGBA')
        for index,f in enumerate(part['frames']):
            frame=Image.new('RGBA',(224,144));frame.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']))
            before=np.asarray(frame);coverage=skin_coverage(frame);assert np.count_nonzero(coverage)>15,(body,group,index,'Missing skin coverage')
            for key in PALETTES:
                tinted=apply_skin_palette(frame,key);after=np.asarray(tinted)
                assert np.array_equal(after[:,:,3],before[:,:,3]),(body,group,index,key,'Alpha changed')
                assert tinted.getbbox()==frame.getbbox(),(body,group,index,key,'Geometry changed')
                diff=np.any(after[:,:,:3]!=before[:,:,:3],axis=2)
                assert not np.any(diff&(coverage==0)),(body,group,index,key,'Changed cloth/ink')
                if key=='original':assert not np.any(diff)
                else:assert np.any(diff);changed+=int(diff.sum())
                # Mirroring a finished skin has exactly the same result.
                if index==0:assert apply_skin_palette(ImageOps.mirror(frame),key).tobytes()==ImageOps.mirror(tinted).tobytes()
                variants+=1
            poses+=1
assert poses==984 and variants==11808
result={'bodies':6,'poses':poses,'tone_options':12,'pose_tone_combinations':variants,'changed_skin_pixels_checked':changed,'alpha_and_geometry_preserved':True,'cloth_ink_and_transparency_protected':True,'strictly_increasing_shading_ramps':True,'runtime_recoloring':False}
(OUT/'palette-tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
