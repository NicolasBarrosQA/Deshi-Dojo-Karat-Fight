"""Extract actual rear skull references; no generated body is imported."""
import json
from pathlib import Path
from PIL import Image
from prepare_hair_bindings import animations
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'assets/source/hair-rebuild-v2'
poses=animations();bindings=json.loads((ROOT/'assets/hair-bindings.json').read_text())
order=['adult','teen','child','adult_female','teen_female','child_female']
sheet=Image.new('RGBA',(1536,1024));anchors={}
for i,body in enumerate(order):
    cx,cy=map(round,bindings[body]['base'][57]['center']);anchors[body]=[cx,cy]
    crop=poses[body]['base'][57].crop((cx-32,cy-28,cx+32,cy+36)).resize((512,512),Image.Resampling.NEAREST)
    sheet.paste(crop,(i%3*512,i//3*512))
sheet.save(folder/'six-actual-rear-heads-reference.png')
(folder/'rear-reference-landmarks.json').write_text(json.dumps(anchors,indent=2)+'\n')
