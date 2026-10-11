"""Actual delivered .lutro frames driven by two RETROPAD ports; no overlays."""
import hashlib,json
from pathlib import Path
from PIL import Image
from native_host import Native
HERE=Path(__file__).resolve().parents[1]
tech=json.loads((HERE/'assets/techniques.json').read_text())['techniques']
def controls(id,side=0):
 action=1 if tech[id]['kind']=='defense' else 0 if id in ('gyaku','oi','jodan') else 8
 keys=[(side,action)]
 direction={'age':4,'gedan':5,'soto':7 if side==0 else 6,'uchi':6 if side==0 else 7,'jodan':4,'oi':7,'mae_low':5,'mawashi':7}.get(id)
 if direction is not None:keys.append((side,direction))
 return keys
record={};allframes=[]
for id in ('age','gedan','soto','uchi','gyaku','oi','jodan','mae','mae_low','mawashi'):
 frames=[]
 with Native(HERE/'dist/deshi-dojo-visual.lutro') as core:
  core.step(40 if id in ('mae_low','mawashi') else 47,[(0,7),(1,6)]);core.step(2)
  t=tech[id];defense=t['kind']=='defense'
  for n in range(75):
   keys=controls(id) if defense and 2<=n<50 or not defense and n in (2,3) else []
   if defense and n in (20,21):keys+=controls('jodan' if id=='age' else 'mae_low' if id=='gedan' else 'gyaku',1)
   core.step(1,keys)
   if n%2==0:frames.append(core.frame.resize((768,448),Image.Resampling.NEAREST))
   if n==14 and defense or n==t['windup']+4 and not defense:
    core.frame.save(HERE/'docs'/f'{id}.png')
    core.frame.resize((1152,672),Image.Resampling.NEAREST).save(HERE/'docs'/f'{id}-3x.png')
  record[id]=len(frames)
 allframes.extend(frames)
 if defense:
  frames[0].save(HERE/'docs'/f'{id}.gif',save_all=True,append_images=frames[1:],duration=80,loop=0,optimize=True)
allframes[0].save(HERE/'docs/fundamentos.gif',save_all=True,append_images=allframes[1:],duration=70,loop=0,optimize=True)
report={'cart_sha256':hashlib.sha256((HERE/'dist/deshi-dojo-visual.lutro').read_bytes()).hexdigest(),
 'techniques':record,'technique_ticks':750,'total_ticks':1226,'sample_every_ticks':2,'gif_presentation':'slowed 70/80ms per sampled frame; simulation remains 60Hz','instrumentation':False}
(HERE/'docs/capture-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
