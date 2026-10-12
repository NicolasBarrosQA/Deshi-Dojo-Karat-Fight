"""Encode captured game PNGs without inventing, redrawing or interpolating frames."""
from pathlib import Path
import json,hashlib
from PIL import Image
HERE=Path(__file__).resolve().parents[1];out=HERE/'docs/special-captures'
capture=json.loads((out/'capture-results.json').read_text())
assert capture['html_sha256']==hashlib.sha256((HERE/'dist/deshi-dojo-visual.html').read_bytes()).hexdigest(),'Capture belongs to another game build'
result={'html_sha256':capture['html_sha256'],'gifs':{}}
for folder in sorted(p for p in out.iterdir() if p.is_dir()):
 if folder.name not in capture['sequences']:continue
 trace=json.loads((folder/'trace.json').read_text());sources=[folder/f"{r['frame']:04}.png" for r in trace]
 frames=[Image.open(p).convert('RGB').resize((768,448),Image.Resampling.NEAREST).quantize(colors=256,method=Image.Quantize.FASTOCTREE) for p in sources]
 if frames:
  target=out/(folder.name+'.gif');frames[0].save(target,save_all=True,append_images=frames[1:],duration=[(60,70,70)[i%3] for i in range(len(frames))],loop=0,optimize=False,disposal=2)
  result['gifs'][folder.name]={'source_frames':len(frames),'encoded_frames':Image.open(target).n_frames,'gif_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'captured_pngs_sha256':hashlib.sha256(b''.join(hashlib.sha256(p.read_bytes()).digest() for p in sources)).hexdigest()}
(out/'gif-results.json').write_text(json.dumps(result,indent=2)+'\n')
print('Actual game captures encoded:',len(list(out.glob('*.gif'))))
