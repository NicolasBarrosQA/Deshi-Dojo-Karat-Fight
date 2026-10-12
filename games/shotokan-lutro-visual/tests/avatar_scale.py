"""Scale regression: exposed neck and folded legs must not shrink a fighter."""
import sys,json,math
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from avatar_set_import import cranial_width,UPRIGHT,BODIES
def fixture(neck,legs):
    im=Image.new('RGBA',(140,220));d=ImageDraw.Draw(im)
    d.ellipse((45,5,95,65),fill=(220,160,115,255));d.rectangle((60,50,80,65+neck),fill=(220,160,115,255))
    d.rectangle((35,66+neck,105,120+neck),fill=(240,240,245,255));d.rectangle((35,120+neck,55,min(215,120+neck+legs)),fill=(240,240,245,255))
    return im
assert abs(cranial_width(fixture(5,60))-cranial_width(fixture(40,20)))<=1
report=json.loads((ROOT/'docs/avatar-set-v3/import-report.json').read_text());assert not report['quality_errors']
air=0
for body in report['bodies']:
    height=BODIES[body['body']][1]
    for sheet in body['sheets']:
        for f in sheet['frames']:
            assert f['scale_reference'].startswith('upright body')
            if sheet['group'] in ('base-64','base-73'):
                target=f['target_cranial_width'];actual=f['cranial_width']*f['scale']
                assert abs(actual-target)<=target*.051,(body['body'],sheet['group'],actual,target)
                air+=1
        if sheet['group'] in UPRIGHT:
            sizes=[sheet['frames'][i]['bounds'][3]-sheet['frames'][i]['bounds'][1] for i in UPRIGHT[sheet['group']]]
            assert all(height*.88<=h<=height*1.12 for h in sizes),(body['body'],sheet['group'],sizes,height)
assert air==108
print('PASS neck/leg isolation, 108 airborne scale references and upright heights on six bodies')
