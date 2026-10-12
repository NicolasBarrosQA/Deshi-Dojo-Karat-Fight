"""Independently audit every new neutral frame, palette, mirror and package input."""
import argparse,json,sys,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageChops
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from character_registry import DEFAULT,validate
from compile_character import transform

def read(path):return json.loads(path.read_text(encoding='utf8'))
def main(staged=False):
    directory=ROOT/'.runtime/avatar-set-v3' if staged else ROOT/'assets'
    assets=directory/'assets' if staged else ROOT/'src/assets'
    base=read(directory/'character-assets.json');special=read(directory/'special-assets.json')
    config=read(ROOT/'assets/characters.json');report=read(ROOT/'docs/avatar-set-v3/import-report.json')
    assert not report['missing_sheets'] and not report.get('quality_errors');assert len(base)==len(special)==6
    cache={};poses=palettes=variants=0;native_bytes=0
    def unpack(part,side='right'):
        name=part[side]
        if name not in cache:
            image=Image.open(assets/(name+'.png')).convert('RGBA')
            assert image.size==(part['width'],part['height'])
            assert set(image.getchannel('A').tobytes())<={0,255}
            cache[name]=image
        atlas=cache[name];result=[]
        for f in part['frames']:
            assert 0<=f['sx']<=atlas.width-f['w'] and 0<=f['sy']<=atlas.height-f['h']
            frame=Image.new('RGBA',(224,144))
            frame.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'] if side=='right' else 224-f['x']-f['w'],f['y']))
            result.append(frame)
        return result
    full_guards={}
    for body,b in base.items():
        assert b['revision']=='neutral-2d-v3'
        assert len(b['bounds'])==92 and len(special[body])==8
        validate({'id':'neutral-test','name':'Neutral Test','body':body,'belt':'branca'},config,base)
        assert set(b['parts']['face'])==set(b['parts']['hair'])=={'default'}
        for layer in ('face','hair'):
            assert not any(f.getbbox() for f in unpack(b['parts'][layer]['default'])),(body,layer,'legacy head survived')
        animations={'base':{'body':b['parts']['body']['default'],'belts':b['parts']['belt'],'bounds':b['bounds']},**special[body]}
        for group,a in animations.items():
            count=92 if group=='base' else 9
            bodies=unpack(a['body']);mirrors=unpack(a['body'],'left');cloth=unpack(a['belts']['branca'])
            assert len(bodies)==len(cloth)==count
            for i,(frame,mirror,belt) in enumerate(zip(bodies,mirrors,cloth)):
                assert ImageOps.mirror(frame).tobytes()==mirror.tobytes(),(body,group,i,'mirror')
                assert not ImageChops.multiply(frame.getchannel('A'),belt.getchannel('A')).getbbox(),(body,group,i,'belt/body overlap')
                hidden=read(ROOT/'assets/source/avatar-set-v3/occlusions.json').get(body+'/'+group,{}).get('cells',[])
                if i in hidden:assert not belt.getbbox(),(body,group,i,'occluded belt incorrectly painted')
                else:assert belt.getbbox() and sum(v>0 for v in belt.getchannel('A').tobytes())>=5,(body,group,i,'missing visible belt')
                whole=Image.alpha_composite(frame,belt);bbox=whole.getbbox()
                assert list(bbox)==a['bounds'][i] and bbox[3]==143,(body,group,i,'floor')
                assert 0<=bbox[0]<bbox[2]<=224 and 0<=bbox[1]<bbox[3]<=144
                for height in (.94,1,1.04):
                    for build in ('leve','medio','forte'):
                        transform(whole,{**DEFAULT,'height':height,'build':build},bbox);variants+=1
                # Chroma markers must never survive into the deployed image.
                assert not any(alpha and r>g*1.45 and b>g*1.25 and r>80 and b>60 for r,g,b,alpha in whole.getdata()),(body,group,i,'pink marker')
                poses+=1
                if group=='base' and i==0:full_guards[body]=whole
            for key,p in a['belts'].items():
                colored=unpack(p);opposite=unpack(p,'left')
                for i,(c,m,white,bodyframe) in enumerate(zip(colored,opposite,cloth,bodies)):
                    assert c.getchannel('A').tobytes()==white.getchannel('A').tobytes(),(body,group,i,key,'belt shape')
                    assert ImageOps.mirror(c).tobytes()==m.tobytes()
                    original=Image.alpha_composite(bodyframe,white).convert('RGB');other=Image.alpha_composite(bodyframe,c).convert('RGB')
                    channels=ImageChops.difference(original,other).split()
                    changed=ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),channels[2]).point(lambda v:255 if v else 0)
                    assert not ImageChops.subtract(changed,white.getchannel('A')).getbbox(),(body,group,i,key,'escaped cloth')
                    palettes+=1
                native_bytes+=p['decoded_bytes']
            native_bytes+=a['body']['decoded_bytes']
    for age in ('adult','teen','child'):
        assert full_guards[age].tobytes()!=full_guards[age+'_female'].tobytes(),(age,'same body used for both sexes')
    assert poses==984 and palettes==7872 and variants==8856
    if not staged:
        assert len(config['students'])==6
        assert not any(s.get('identity') or s.get('visual') for s in config['students'].values())
        assert read(ROOT/'assets/character-identities.json')['bodies']=={}
    result={'poses':poses,'belt_pose_combinations':palettes,'proportion_checks':variants,
        'six_bases_distinct':True,'binary_alpha':True,'exact_mirrors':True,'belt_pixels_isolated':True,
        'all_native_atlases_bytes':native_bytes,'native_device_tested':False,'staged':staged}
    (ROOT/'docs/avatar-set-v3/asset-tests.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--staged',action='store_true');a=p.parse_args();main(a.staged)
