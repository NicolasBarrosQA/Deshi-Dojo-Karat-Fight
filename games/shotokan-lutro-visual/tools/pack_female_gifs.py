"""Pack only the real offline gameplay frames recorded by female_bodies.cjs."""
import json,hashlib
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parents[1];OUT=HERE/'docs/female-bodies'
trace=json.loads((OUT/'capture-traces.json').read_text())
assert hashlib.sha256((HERE/'dist/deshi-dojo-visual.html').read_bytes()).hexdigest()==trace['artifact_sha256'],'Capture must match delivered game'
results={}
for body,records in trace['frames'].items():
    assert records and any('ashi_barai' in r['state'] for r in records) and any('ashi_finish' in r['state'] for r in records)
    frames=[]
    for r in records:
        im=Image.open(HERE/'.runtime/female-captures'/body/r['file']).convert('RGB');assert im.size==(384,224)
        frames.append(im.resize((768,448),Image.Resampling.NEAREST).quantize(colors=256))
    path=OUT/(body+'-ashi-sequence.gif');frames[0].save(path,save_all=True,append_images=frames[1:],duration=[60 if i%3==0 else 70 for i in range(len(frames))],loop=0,disposal=2,optimize=False)
    results[body]={'file':path.name,'recorded_frames':len(records),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'game_sha256':trace['artifact_sha256'],'playback':'0.5x; every 2 ticks from the real game'}
(OUT/'gif-results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
