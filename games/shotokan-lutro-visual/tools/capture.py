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
def two_players(core):
 # Delivered game starts solo. Choose humans through the real native menu.
 core.step(2,[(0,2)]);core.step(2)
 for _ in range(3):core.step(2,[(0,5)]);core.step(2)
 core.step(2,[(0,0)]);core.step(2)
 return 20
record={};allframes=[];total_ticks=0
for id in data['order']:
 frames=[];t=tech[id];defense=t['kind']=='defense';air=t.get('air',False)
 distance=88 if defense else max(88,int((t['hit']['near']+t['hit']['far'])/2))
 approach=max(0,int((176-distance)/3.8))
 with Native(HERE/'dist/deshi-dojo-visual.lutro') as core:
  total_ticks+=two_players(core)
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
# The same beginner combo as the real input tests, including early buffered presses.
frames=[]
with Native(HERE/'dist/deshi-dojo-visual.lutro') as core:
 total_ticks+=two_players(core)
 core.step(30,[(0,7),(1,6)]);core.step(2);total_ticks+=32
 for n in range(66):
  keys=[(0,0)] if n in (0,1,3,4) else [(0,8)] if n in (12,13) else []
  core.step(1,keys);total_ticks+=1
  if n%2==0:frames.append(core.frame.copy())
frames[0].save(HERE/'docs/renzoku.gif',save_all=True,append_images=frames[1:],duration=55,loop=0,optimize=True)
report={'cart_sha256':hashlib.sha256((HERE/'dist/deshi-dojo-visual.lutro').read_bytes()).hexdigest(),
 'techniques':record,'technique_ticks':80*len(data['order']),'total_ticks':total_ticks,'sample_every_ticks':2,
 'gif_presentation':'native resolution, slowed 70/80ms per sampled frame; simulation remains 60Hz','instrumentation':False,
 'renzoku_capture':'Soco > soco > chute, early real presses; native/browser tests independently require three actual hits'}
(HERE/'docs/capture-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
