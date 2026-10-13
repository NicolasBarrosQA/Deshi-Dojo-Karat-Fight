"""Actual neutral skulls as art references, not generic mannequin templates."""
import json
from pathlib import Path
from PIL import Image,ImageDraw
from prepare_hair_bindings import animations
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'assets/source/hair-rebuild-v2';folder.mkdir(exist_ok=True)
poses=animations();bindings=json.loads((ROOT/'assets/hair-bindings.json').read_text())
manual_guard={'adult':[115,25],'teen':[116,41],'child':[114,61],'adult_female':[110,24],'teen_female':[112,42],'child_female':[112,61]}
for body,(cx,cy) in manual_guard.items():
    # Constant pixel coordinates, reviewed on the approved bald guard drawings.
    crop=poses[body]['base'][0].crop((cx-32,cy-28,cx+32,cy+36))
    crop.resize((512,512),Image.Resampling.NEAREST).save(folder/(body+'-guard-reference.png'))
out=ROOT/'docs/hair-rebuild-v2';out.mkdir(exist_ok=True)
sheet=Image.new('RGB',(6*176,6*174),'#243640');draw=ImageDraw.Draw(sheet)
samples=[('base',0),('ura_mawashi',4),('nidan',2),('base',61),('base',84),('knockdown',4)]
for row,(body,groups) in enumerate(poses.items()):
    for col,(group,index) in enumerate(samples):
        b=bindings[body][group][index];cx,cy=b['center'];im=groups[group][index]
        crop=im.crop((round(cx)-24,round(cy)-24,round(cx)+24,round(cy)+28)).resize((144,156),Image.Resampling.NEAREST)
        x=col*176;y=row*174;sheet.paste(crop,(x,y+18),crop)
        draw.text((x,y),body+'/'+group+str(index+1),fill='#e8c88a')
        # Yellow: old skin-radius measurement, retained only to explain the bug.
        rx=b['width']/2*3;ry=b['height']/2*3
        draw.ellipse((x+72-rx,y+18+72-ry,x+72+rx,y+18+72+ry),outline='#f4cf32',width=1)
sheet.save(out/'old-skin-radius-audit.png')
(folder/'guard-reference-landmarks.json').write_text(json.dumps(manual_guard,indent=2)+'\n')
print('Six actual skull references and old-fit audit prepared')
