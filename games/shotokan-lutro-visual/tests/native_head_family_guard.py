"""Independent guard crown coverage across both studies and all six skulls."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from prepare_hair_bindings import animations
from head_registration import skin_mask
from hair_art import overlay,PAD
poses=animations();folder=ROOT/'assets/source/hair-rebuild-v2'
anchors=json.loads((folder/'guard-reference-landmarks.json').read_text())
checks=0;pending=[]
for style in ['masculino_curto','feminino_chanel']:
    for body,(cx,cy) in anchors.items():
        hair=Image.open(folder/(style+'-'+body+'-native.png')).convert('RGBA')
        assert hair.size==(64,64)
        p=np.asarray(hair);assert set(np.unique(p[:,:,3]))<={0,255}
        layer=overlay({'body':body,'hair':style,'appearance':{'hair_color':'original'}},'base',0)
        visible=np.asarray(layer)[PAD:,:,3]>0
        base=poses[body]['base'][0];yy,xx=np.indices(visible.shape)
        skull=skin_mask(base)&(abs(xx-cx)<7)&(yy<cy)&(yy>cy-22)
        assert skull.any(),(body,'Missing actual skull fixture')
        top=int(yy[skull].min())
        crown=skull&(yy<top+3)
        assert crown.any(),'The anatomical crown fixture must contain skin'
        exposed=int(np.count_nonzero(crown&~visible))
        if exposed: pending.append({'style':style,'body':body,'exposed_top_skin_pixels':exposed})
        # All material remains near the authored skull, not clothing or hands.
        assert not np.any(visible&((abs(xx-cx)>24)|(yy<cy-22)|(yy>cy+22))), (style,body,'hair material outside head region')
        checks+=1
print('Geometry checked for 12 baked native guard layers')
print(json.dumps({'crown_review_pending':pending}))
sys.exit(1 if pending else 0)
