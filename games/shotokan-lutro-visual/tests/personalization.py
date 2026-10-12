"""Verify every authored pose, attachment partition, mirror and belt palette."""
from pathlib import Path
import json,sys,zipfile
from PIL import Image,ImageOps,ImageChops
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'tools'))
from import_characters import binary
from character_masks import hair_bounds
manifest=json.loads((HERE/'assets/character-assets.json').read_text())
config=json.loads((HERE/'assets/characters.json').read_text())
checks=[];cache={}
def surface(name):
    if name not in cache:
        cache[name]=Image.open(HERE/'src/assets'/(name+'.png')).convert('RGBA')
        assert set(cache[name].getchannel('A').tobytes())<={0,255}
    return cache[name]
def rebuild(body,pose,belt='preta',side='right'):
    out=Image.new('RGBA',(224,144))
    for layer in ('body','belt','face','hair','foreground'):
        part=manifest[body]['parts'][layer][belt if layer=='belt' else 'default'];f=part['frames'][pose]
        crop=surface(part[side]).crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h']))
        x=f['x'] if side=='right' else 224-f['x']-f['w']
        out.alpha_composite(crop,(x,f['y']))
    return out
for body in config['body_order']:
    assert len(manifest[body]['bounds'])==92
    reference=Image.open(HERE/'docs'/f'character-{body}-atlas.png').convert('RGBA')
    cloth=Image.open(HERE/'assets'/f'character-belt-{body}-mask.png').convert('L')
    for pose in range(92):
        r=rebuild(body,pose);l=rebuild(body,pose,side='left')
        original=reference.crop(((pose%4)*224,(pose//4)*144,(pose%4+1)*224,(pose//4+1)*144))
        assert r.tobytes()==binary(original).tobytes(),(body,pose,'layer reconstruction')
        assert l.tobytes()==ImageOps.mirror(r).tobytes(),(body,pose,'mirror drift')
        assert list(r.getbbox())==manifest[body]['bounds'][pose]
        expected_feet=Image.open(HERE/'src/assets'/f'pose-{pose+1:02d}.png').getbbox()[3] if body=='adult' else 143
        assert r.getbbox()[3]==expected_feet,(body,pose,'feet')
        for belt in config['belt_order']:
            colored=rebuild(body,pose,belt)
            assert colored.getchannel('A').tobytes()==r.getchannel('A').tobytes(),(body,pose,belt,'silhouette change')
            mask=cloth.crop(((pose%4)*224,(pose//4)*144,(pose%4+1)*224,(pose//4+1)*144))
            channels=ImageChops.difference(r.convert('RGB'),colored.convert('RGB')).split()
            changed=ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),channels[2]).point(lambda value:255 if value else 0)
            expected_mask=mask if belt!='preta' else Image.new('L',mask.size)
            assert changed.tobytes()==expected_mask.tobytes(),(body,pose,belt,'color escaped cloth or cloth remained black')
        for layer,variants in manifest[body]['parts'].items():
            for part in variants.values():
                assert len(part['frames'])==92
                for side in ('right','left'):
                    surface(part[side])
    checks.append(f'{body}: 92 reconstructed poses, foot anchors verified, exact mirrors, 8 belt silhouettes')
for pose in range(92):
    legacy=binary(Image.open(HERE/'src/assets'/f'pose-{pose+1:02d}.png'))
    assert rebuild('adult',pose).tobytes()==legacy.tobytes(),('adult preservation',pose)
checks.append('Adult layers match all 92 audited source poses, including requested foot corrections')
for body in ('teen','child'):
    head=lambda pose:hair_bounds(rebuild(body,pose))[2]-hair_bounds(rebuild(body,pose))[0]
    import statistics
    standing=statistics.median(head(pose) for pose in range(4))
    jumping=statistics.median(head(pose) for pose in range(60,64))
    assert abs(jumping/standing-1)<=.08,(body,standing,jumping,'grows during jump')
checks.append('Teen and child jumps retain standing head scale within 8%; adult jump pixels remain at native scale; only cloth pixels recolored in all 2208 combinations')
heights=[manifest[b]['bounds'][0][3]-manifest[b]['bounds'][0][1] for b in config['body_order']]
assert heights[0]>heights[1]>heights[2],heights
checks.append('Distinct authored base heights: '+str(heights))
from compile_character import layer_frames
for body in config['body_order']:
    hair_frames=layer_frames(body,'hair','default',manifest)
    width=lambda p:hair_bounds(hair_frames[p])[2]-hair_bounds(hair_frames[p])[0]
    assert abs(width(74)-width(0))<=1,(body,width(74),width(0),'airborne kick head scale')
checks.append('Corrected airborne kick 75 retains standing hair width within one native pixel for all bodies')
import_report=json.loads((HERE/'assets/character-import.json').read_text())
for body in ('teen','child'):
    sources=import_report['bases'][body]['sources']
    assert len(sources)==7 and sum(s['poses'] for s in sources)==92
    assert all(s['poses']<=16 and s['median_source_height']>=160 and 0<s['scale']<=1 and not s['upscaled'] for s in sources)
checks.append('High-resolution child/teen sources: 7 sheets each, no enlargement, at most 16 poses per sheet')
result={'checks':checks,'poses':276,'belt_pose_combinations':2208,'native_parity':'pending: Linux historical core absent on this Windows checkout','raspberry_pi':'pending: ARM, GPIO, memory and performance untested'}
(HERE/'docs/personalization-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
