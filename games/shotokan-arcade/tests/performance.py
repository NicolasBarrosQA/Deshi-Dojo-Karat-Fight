"""Desktop-only comparative CPU timing, including audio, excluding image conversion."""
import ctypes as C
import hashlib,json,statistics,sys,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'prototypes/tic80/tools'))
from legacy_core import Core,VIDEO

def measure(cart):
 core=Core(ROOT/'.cache/tic80-legacy/tic80_libretro.so',cart)
 rendered=0
 @VIDEO
 def video(data,w,h,pitch):
  nonlocal rendered
  assert data and w==256 and h==144;rendered+=1
 core.core.retro_set_video_refresh.argtypes=[VIDEO];core.core.retro_set_video_refresh(video)
 def step(n,keys=()):
  core.buttons.clear()
  for key in keys:core.key(key,True)
  times=[]
  for _ in range(n):
   before=time.perf_counter_ns();core.tick();times.append((time.perf_counter_ns()-before)/1e6)
  return times
 try:
  step(1);step(1,(4,));step(1);step(1,(4,12));step(36)
  samples=[]
  for cycle in range(60):
   samples+=step(50,(3,10))
   samples+=step(1,(4+cycle%4,12+(cycle+2)%4))
   samples+=step(65)
   # Confirmation only after result debounce; otherwise it is a real whiff.
   samples+=step(1,(4,12));samples+=step(1)
  values=sorted(samples)
  return dict(frames=len(samples),rendered=rendered,mean_ms=round(statistics.mean(values),3),
   p95_ms=round(values[int(len(values)*.95)],3),p99_ms=round(values[int(len(values)*.99)],3),
   max_ms=round(values[-1],3),over_16_67_ms=sum(t>1000/60 for t in values),lua_errors=core.errors)
 finally:core.close()
with zipfile.ZipFile(ROOT/'archives/shotokan-arcade-v01.zip') as z:old=z.read('dist/shotokan-arcade.tic')
new=(HERE/'dist/shotokan-arcade.tic').read_bytes()
result=dict(platform='Linux cloud x86-64, historical Lua-only core; no ARM/GPIO validation',
 excludes='Python RGB conversion, Tk display and actual monitor/input latency',
 before_sha256=hashlib.sha256(old).hexdigest(),after_sha256=hashlib.sha256(new).hexdigest(),
 before=measure(old),after=measure(new))
(HERE/'docs/performance-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
