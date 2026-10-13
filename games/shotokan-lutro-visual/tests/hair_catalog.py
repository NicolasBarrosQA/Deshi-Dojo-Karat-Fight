"""Every published style/body/pose; independent material and frame contracts."""
import argparse,hashlib,json,sys,time
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageOps
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from hair_art import styles,beards,apply,overlay,PAD,logical_bounds
from hair_palette import COLORS,recolor
from prepare_hair_bindings import animations
from compile_character import transform
from character_registry import read,validate,visual_key

def run(complete=True):
    start=time.monotonic();hair=styles();facial=beards();counts=Counter(v.get('category','masculino') for v in hair.values())
    if complete:
        legacy=Counter(v.get('category','masculino') for v in hair.values() if not v.get('pose_layers'))
        assert legacy=={'masculino':13,'feminino':10} and len(facial)==6,(legacy,len(facial))
        assert {k for k,v in hair.items() if v.get('available',True)}=={'masculino_curto','feminino_chanel'}
    poses=animations();checks=geometry=materials=0;errors=[];reviews=ROOT/'docs/hair-catalog';reviews.mkdir(parents=True,exist_ok=True)
    # Body scale contracts are independent of the selected hair material.
    for body,groups in poses.items():
        for group,frames in groups.items():
            for i,frame in enumerate(frames):
                padded=Image.new('RGBA',(224,144+PAD));padded.paste(frame,(0,PAD));padded.info['logical_origin_y']=-PAD
                for height in (.94,1,1.04):
                    for build in ('leve','medio','forte'):
                        ap={'height':height,'build':build}
                        assert np.array_equal(np.asarray(transform(padded,ap,frame.getbbox()))[PAD:],np.asarray(transform(frame,ap,frame.getbbox()))),(body,group,i,'scale')
    for kind,catalog in [('hair',hair),('beard',facial)]:
        for style,entry in catalog.items():
            # Every source view and every palette, with exact alpha preservation.
            for view,record in entry['views'].items():
                im=Image.open(ROOT/record['path']).convert('RGBA');original=np.asarray(im);visible=original[:,:,3]>0
                assert set(np.unique(original[:,:,3]))<={0,255}
                assert np.all(original[~visible]==0)
                for color in [*COLORS,'#123abc']:
                    tinted=np.asarray(recolor(im,color));assert np.array_equal(original[:,:,3],tinted[:,:,3])
                    assert np.all(tinted[~visible]==0);materials+=1
            sheet=Image.new('RGB',(12*112,6*120),'#20343e');draw=ImageDraw.Draw(sheet)
            for row,(body,groups) in enumerate(poses.items()):
                reviewed=[]
                student={'body':body,'hair':style if kind=='hair' else 'default','beard':style if kind=='beard' else 'default','appearance':{'hair_color':'branco','beard_color':'grisalho'}}
                for group,frames in groups.items():
                    for i,frame in enumerate(frames):
                        try:
                            layer=overlay(student,group,i,kind);result=apply(frame,student,group,i)
                            src=np.asarray(frame);actual=np.asarray(result)[PAD:];coverage=np.asarray(layer)[PAD:,:,3]>0
                            assert np.array_equal(src[~coverage],actual[~coverage]),'outside material changed'
                            assert set(np.unique(np.asarray(result)[:,:,3]))<={0,255},'alpha fringe'
                            assert logical_bounds(result)[3]<=144,'below floor'
                            for height in (.94,1,1.04):
                                for build in ('leve','medio','forte'):
                                    b=logical_bounds(transform(result,{'height':height,'build':build},frame.getbbox()))
                                    assert b[0]>=0 and b[2]<=224 and b[3]<=144,'proportion clipping'
                                    geometry+=1
                            checks+=1
                            if (group=='base' and i in (0,8,14,58,61,62,84)) or (group=='knockdown' and i in (2,4,5)) or (group=='ceremony' and i==2) or (group=='ushiro' and i==3):reviewed.append((group,i,result))
                        except Exception as e:
                            errors.append({'kind':kind,'style':style,'body':body,'group':group,'pose':i+1,'error':str(e)})
                for col,(group,i,result) in enumerate(reviewed[:12]):
                    binding=read(ROOT/'assets/hair-bindings.json')[body][group][i];cx,cy=binding['center']
                    crop=result.crop((round(cx)-25,round(cy)+PAD-25,round(cx)+25,round(cy)+PAD+30)).resize((100,110),Image.Resampling.NEAREST)
                    x=col*112;y=row*120;sheet.paste(crop,(x,y+10),crop);draw.text((x,y),body+'/'+group+str(i+1),fill='white')
            sheet.save(reviews/(kind+'-'+style+'.png'));print(kind,style,checks,'cases',len(errors),'errors',flush=True)
    config=read(ROOT/'assets/characters.json');manifest=read(ROOT/'assets/character-assets.json');old=config['students']['demo-adult']
    assert visual_key(validate(old,config,manifest))==visual_key(validate({**old,'beard':'default','appearance':{**old['appearance'],'beard_color':'original'}},config,manifest)),'legacy cache keys changed'
    for style in facial:
        s=validate({**old,'beard':style,'appearance':{**old['appearance'],'beard_color':'#AbCd12'}},config,manifest)
        assert s['appearance']['beard_color']=='#abcd12'
        assert visual_key(s)!=visual_key(validate(old,config,manifest))
    report={'complete_catalog_required':complete,'hair_counts':dict(counts),'beards':len(facial),'pose_cases':checks,'proportion_cases':geometry,'material_cases':materials,'errors':errors,'elapsed_seconds':round(time.monotonic()-start,1)}
    (reviews/'tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({**report,'errors':len(errors)}));assert not errors,f'{len(errors)} fitting errors; see docs/hair-catalog/tests.json'

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--partial',action='store_true');args=parser.parse_args();run(not args.partial)
