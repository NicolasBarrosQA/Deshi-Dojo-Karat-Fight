"""Extract authored hair material and place it in its original native head crop."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from native_hair_material import extract
from prepare_hair_bindings import animations
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'assets/source/hair-rebuild-v2';out=ROOT/'docs/hair-rebuild-v2'
out.mkdir(exist_ok=True);poses=animations();anchors=json.loads((source/'guard-reference-landmarks.json').read_text())
sheet=Image.new('RGB',(896,580),'#243640');draw=ImageDraw.Draw(sheet);report=[]
for col,(body,label) in enumerate([('adult','MASCULINO'),('adult_female','FEMININO')]):
    with Image.open(source/(body+'-green-study.png')) as im:im=im.convert('RGBA').resize((64,64),Image.Resampling.NEAREST)
    hair=extract(im);hair.save(source/(body+'-native-guard-hair.png'))
    cx,cy=anchors[body];origin=(cx-32,cy-28)
    base=poses[body]['base'][0];overlay=Image.new('RGBA',base.size);overlay.paste(hair,origin);result=Image.alpha_composite(base,overlay)
    visible=np.asarray(overlay)[:,:,3]>0;before=np.asarray(base);after=np.asarray(result)
    assert np.array_equal(before[~visible],after[~visible]),'Original sprite pixels changed outside the authored hair'
    x=col*448;draw.text((x+18,12),label+' - DESENHO SOBRE A CABECA REAL',fill='#edce92')
    picture=result.resize((448,288),Image.Resampling.NEAREST);sheet.paste(picture,(x,44),picture)
    draw.text((x+18,339),'DETALHE 4x - SEM MOLDE GENERICO',fill='#edce92')
    patch=result.crop((cx-26,cy-25,cx+26,cy+29)).resize((208,216),Image.Resampling.NEAREST);sheet.paste(patch,(x+120,358),patch)
    report.append({'body':body,'method':'authored-on-native-head-crop','crop_origin':origin,'visible_hair_pixels':int(visible.sum()),'original_body_preserved_outside_hair':True})
sheet.save(out/'direct-male-female-guard.png')
(out/'direct-studies.json').write_text(json.dumps({'status':'unapproved_guard_studies','old_radius_fitting_used':False,'studies':report},indent=2)+'\n')
print('Male and female studies rendered at native coordinates; original bodies preserved')
