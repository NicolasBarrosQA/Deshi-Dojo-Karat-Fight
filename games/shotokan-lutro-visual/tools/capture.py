"""Actual delivered .lutro frames driven by two RETROPAD ports; no overlays."""
import hashlib,json
from pathlib import Path
from PIL import Image
from native_host import Native
HERE=Path(__file__).resolve().parents[1]
data=json.loads((HERE/'assets/techniques.json').read_text(encoding='utf-8'));tech=data['techniques']
def controls(id,side=0):
 t=tech[id];keys=[(side,{'defense':1,'punch':0,'kick':8}[t['button']])]
 for d in t['direction'].split('_'):
  direction={'up':4,'down':5,'forward':7 if side==0 else 6,'back':6 if side==0 else 7}.get(d)
  if direction is not None:keys.append((side,direction))
 return keys
record={};allframes=[];total_ticks=0
for id in data['order']:
 frames=[];t=tech[id];defense=t['kind']=='defense';air=t.get('air',False)
 distance=67 if defense else int((t['hit']['near']+t['hit']['far'])/2)
 approach=max(0,int((176-distance)/2.4))
 with Native(HERE/'dist/deshi-dojo-visual.lutro') as core:
  core.step(approach,[(0,7),(1,6)]);core.step(2);total_ticks+=approach+2
  for n in range(80):
   trigger=12 if air else 2
   keys=controls(id) if defense and trigger<=n<50 or not defense and n in (trigger,trigger+1) else []
   if air and n in (2,3):keys=[(0,4)]
   if defense and n in (20,21):keys+=controls('jodan' if id=='age' else 'mae_low' if id=='gedan' else 'gyaku',1)
   core.step(1,keys);total_ticks+=1
   if n%2==0:frames.append(core.frame.copy())
   if n==(14 if defense else trigger+t['windup']+2):
    core.frame.save(HERE/'docs'/f'{id}.png')
    core.frame.resize((1152,672),Image.Resampling.NEAREST).save(HERE/'docs'/f'{id}-3x.png')
  record[id]=len(frames)
 allframes.extend(frames)
 if defense:
  enlarged=[f.resize((768,448),Image.Resampling.NEAREST) for f in frames]
  enlarged[0].save(HERE/'docs'/f'{id}.gif',save_all=True,append_images=enlarged[1:],duration=80,loop=0,optimize=True)
allframes[0].save(HERE/'docs/fundamentos.gif',save_all=True,append_images=allframes[1:],duration=70,loop=0,optimize=True)
# A real three-technique sequence at contact distance, queued in recovery.
frames=[]
with Native(HERE/'dist/deshi-dojo-visual.lutro') as core:
 core.step(44,[(0,7),(1,6)]);core.step(2);total_ticks+=46
 for id in ('kizami','gyaku','mae'):
  duration=sum(tech[id]['durations'])+4 # one contact freeze at this distance
  for n in range(duration):
   # Physical presses preserve full recovery; tests also exercise buffered links.
   keys=controls(id) if n<2 else []
   core.step(1,keys);total_ticks+=1
   if n%2==0:frames.append(core.frame.copy())
 # Keep a separate GIF of actual sequential inputs; native tests prove buffer links.
frames[0].save(HERE/'docs/renzoku.gif',save_all=True,append_images=frames[1:],duration=65,loop=0,optimize=True)
report={'cart_sha256':hashlib.sha256((HERE/'dist/deshi-dojo-visual.lutro').read_bytes()).hexdigest(),
 'techniques':record,'technique_ticks':80*len(data['order']),'total_ticks':total_ticks,'sample_every_ticks':2,
 'gif_presentation':'native resolution, slowed 70/80ms per sampled frame; simulation remains 60Hz','instrumentation':False,
 'renzoku_capture':'Sequential physical inputs; buffer linkage independently exercised by tests/native.py'}
(HERE/'docs/capture-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
