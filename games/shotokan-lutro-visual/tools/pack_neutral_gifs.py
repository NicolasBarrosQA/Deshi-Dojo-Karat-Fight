"""Package ONLY traced real-game frames; no generated or synthetic animations."""
from pathlib import Path
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/avatar-set-v3'
data=json.loads((OUT/'capture-traces.json').read_text())
assert data['artifact_sha256']==hashlib.sha256((ROOT/'dist/deshi-dojo-visual.html').read_bytes()).hexdigest(),'Capture belongs to another game build'
results=[]
for sequence,trace in data['frames'].items():
    frames=[Image.open(ROOT/'.runtime/neutral-captures'/sequence/f['file']).convert('RGB').resize((768,448),Image.Resampling.NEAREST).quantize(colors=256,method=Image.Quantize.FASTOCTREE) for f in trace]
    assert len(frames)>80
    path=OUT/(sequence+'-ashi-sequence.gif')
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=[(60,70,70)[i%3] for i in range(len(frames))],loop=0,disposal=2,optimize=False)
    results.append({'sequence':sequence,'frames':len(frames),'file':path.name,'source_html_sha256':data['artifact_sha256']})
(OUT/'gif-results.json').write_text(json.dumps(results,indent=2)+'\n')
print('Packed',len(results),'real-game GIFs with verified build hash; playback 0.5x')
