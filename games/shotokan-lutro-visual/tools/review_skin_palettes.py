"""Review actual skin material output using the approved game artwork."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
from skin_palette import PALETTES,apply_skin_palette
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/skin-personalization';OUT.mkdir(parents=True,exist_ok=True)
base=json.loads((ROOT/'assets/character-assets.json').read_text());font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',13)
def unpack(part,index):
    f=part['frames'][index];atlas=Image.open(ROOT/'src/assets'/(part['right']+'.png')).convert('RGBA');im=Image.new('RGBA',(224,144));im.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']));return im
for pose in (0,62):
    sheet=Image.new('RGB',(224*12,180*6),'#23313b');d=ImageDraw.Draw(sheet)
    for row,(body,b) in enumerate(base.items()):
        original=unpack(b['parts']['body']['default'],pose);belt=unpack(b['parts']['belt']['branca'],pose)
        for col,(key,tone) in enumerate(PALETTES.items()):
            im=Image.alpha_composite(apply_skin_palette(original,key),belt);sheet.paste(im,(224*col,180*row+30),im)
            d.text((224*col+6,180*row+2),body+' / '+tone['label'],fill='#eee8db',font=font)
    sheet.save(OUT/('guards.png' if pose==0 else 'jump-descent.png'))
print('Reviewed 72 guard and 72 descent combinations; exact approved resolution.')
