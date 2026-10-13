"""Encode only PNG frames captured from the real offline game by the E2E."""
import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];DOC=ROOT/'docs/hair-rebuild-v2';report={}
for body in ['adult','teen','child','adult_female','teen_female','child_female']:
    folder=ROOT/'.runtime/native-hair-captures'/body;paths=sorted(folder.glob('*.png'))
    assert len(paths)==61,(body,'Capture must contain all 61 actual game frames')
    images=[Image.open(p).convert('RGB') for p in paths]
    target=DOC/('runtime-'+body+'.gif')
    frames=[im.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE) for im in images]
    frames[0].save(target,save_all=True,append_images=frames[1:],duration=70,loop=0,optimize=False,disposal=2)
    report[body]={'source':'tests/native_hair_editor.cjs, canvas #game, actual offline runtime','ticks':'0..240, step 4 at 60 Hz','actions':['jump','nidan','ushiro'],'cuts':['masculino_curto','feminino_chanel'],'source_png_sha256':[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths],'gif':target.name,'capture_frames':len(paths)}
    print(target.name)
(DOC/'runtime-capture-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
