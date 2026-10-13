"""Study two actual-head hair families on all six original neutral guard poses."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from native_hair_material import extract
from head_registration import skin_mask
from prepare_hair_bindings import animations
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'assets/source/hair-rebuild-v2';out=ROOT/'docs/hair-rebuild-v2'
out.mkdir(exist_ok=True)
order=['adult','teen','child','adult_female','teen_female','child_female']
labels=['ADULTO M','ADOLESCENTE M','CRIANCA M','ADULTA F','ADOLESCENTE F','CRIANCA F']
poses=animations();anchors=json.loads((source/'guard-reference-landmarks.json').read_text())
sheet=Image.new('RGB',(936,432),'#243640');draw=ImageDraw.Draw(sheet);checks=[]
for row,(name,label) in enumerate([('masculino_curto','CORTE MASCULINO - ESTUDO EM GUARDA'),('feminino_chanel','CORTE FEMININO - ESTUDO EM GUARDA')]):
    with Image.open(source/(name+'-six-heads.png')) as im:paint=im.convert('RGBA')
    assert paint.size==(1536,1024),'Authored reference grid changed; review alignment before extraction'
    draw.text((8,row*216+3),label,fill='#edce92')
    for col,body in enumerate(order):
        raw=paint.crop((col%3*512,col//3*512,(col%3+1)*512,(col//3+1)*512)).resize((64,64),Image.Resampling.NEAREST)
        hair=extract(raw);hair.save(source/(name+'-'+body+'-native.png'))
        cx,cy=anchors[body];base=poses[body]['base'][0];layer=Image.new('RGBA',base.size);layer.paste(hair,(cx-32,cy-28));result=Image.alpha_composite(base,layer)
        before=np.asarray(base);after=np.asarray(result);coverage=np.asarray(layer)[:,:,3]>0
        assert np.array_equal(before[~coverage],after[~coverage]),'Original body changed outside new hair'
        yy,xx=np.indices(coverage.shape);skull=skin_mask(base)&(np.abs(xx-cx)<7)&(yy<cy)&(yy>cy-22)
        assert skull.any(),'Missing actual skull fixture'
        crown=skull&(yy<int(yy[skull].min())+3)
        exposed=int(np.count_nonzero(crown&~coverage))
        checks.append({'style':name,'body':body,'visible_hair_pixels':int(coverage.sum()),'original_body_preserved':True,'crown_pixels':int(crown.sum()),'exposed_crown_pixels':exposed})
        crop=result.crop((cx-24,cy-23,cx+24,cy+31)).resize((144,162),Image.Resampling.NEAREST)
        x=col*156;y=row*216+30;sheet.paste(crop,(x,y),crop);draw.text((x+3,y+170),labels[col],fill='white')
sheet.save(out/'native-six-head-studies.png')
(out/'native-family-checks.json').write_text(json.dumps({'status':'unapproved_guard_studies','old_radius_fitting_used':False,'checks':checks},indent=2)+'\n')
print(json.dumps({'guard_samples':len(checks),'body_pixels_preserved':True,'crown_exposure':[(c['style'],c['body'],c['exposed_crown_pixels']) for c in checks]}))
