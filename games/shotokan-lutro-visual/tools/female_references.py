"""Reference contact sheets of existing choreography; never generate anatomy."""
import json
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parents[1]
OUT=HERE/'assets/source/female';OUT.mkdir(parents=True,exist_ok=True)
def frame(atlas,i):return atlas.crop(((i%4)*224,(i//4)*144,(i%4+1)*224,(i//4+1)*144))
def packed(part,i):
    r=part['frames'][i];im=Image.open(HERE/'src/assets'/(part['right']+'.png')).convert('RGBA')
    c=im.crop((r['sx'],r['sy'],r['sx']+r['w'],r['sy']+r['h']))
    f=Image.new('RGBA',(224,144));f.paste(c,(r['x'],r['y']));return f
def sheet(name,rows):
    out=Image.new('RGBA',(224*9,144*3))
    for y,row in enumerate(rows):
        for x,f in enumerate(row):out.paste(f,(x*224,y*144))
    out.resize((4032,864),Image.Resampling.NEAREST).save(OUT/(name+'-reference.png'))
atlases=[Image.open(HERE/'docs'/f'character-{b}-atlas.png').convert('RGBA') for b in ('adult','teen','child')]
for start in range(0,92,9):
    sheet(f'base-{start+1:02d}',[[frame(a,min(i,91)) for i in range(start,start+9)] for a in atlases])
special=json.loads((HERE/'assets/special-assets.json').read_text())
for group in special['adult']:
    sheet(group,[[Image.alpha_composite(packed(special[b][group]['body'],i),packed(special[b][group]['belts']['preta'],i)) for i in range(9)] for b in ('adult','teen','child')])
print('Created 19 reference sheets, 27 cells each, last base sheet padded.')
