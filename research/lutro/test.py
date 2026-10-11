"""Read-only core capability test: native PNG colors/resolution and 2 input ports."""
import ctypes as C
import json,sys,time
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'prototypes/tic80/tools'))
from legacy_core import ENV,VIDEO,LOG,BATCH,AUDIO,POLL,INPUT,Game
core=C.CDLL(str(ROOT/'.cache/lutro-research/source/lutro_libretro.so'))
buttons=set();errors=[];frame=None;frame_time=None
TIMER=C.CFUNCTYPE(C.c_int64);FRAME=C.CFUNCTYPE(None,C.c_int64)
clock=TIMER(lambda:time.monotonic_ns()//1000)
class Perf(C.Structure):_fields_=[('clock',C.c_void_p)]+[(name,C.c_void_p) for name in ['features','counter','register','start','stop','log']]
@LOG
def logger(level,message):
 if level>=3:errors.append(message.decode(errors='replace'))
@ENV
def env(command,data):
 global frame_time
 if command==27:C.cast(data,C.POINTER(C.c_void_p))[0]=C.cast(logger,C.c_void_p).value;return True
 if command==28:C.cast(data,C.POINTER(Perf))[0]=Perf(C.cast(clock,C.c_void_p).value,None,None,None,None,None,None);return True
 if command==10:return C.cast(data,C.POINTER(C.c_int))[0]==1
 if command==21:frame_time=FRAME(C.cast(data,C.POINTER(C.c_void_p))[0]);return True
 return False
@VIDEO
def video(data,w,h,pitch):
 global frame
 raw=C.string_at(data,pitch*h);frame=Image.frombytes('RGB',(w,h),raw,'raw','BGRX',pitch)
@INPUT
def inputs(port,device,index,key):return int(device==1 and (port,key) in buttons)
callbacks=[('environment',ENV,env),('video_refresh',VIDEO,video),('audio_sample',AUDIO,AUDIO(lambda l,r:None)),('audio_sample_batch',BATCH,BATCH(lambda data,n:n)),('input_poll',POLL,POLL(lambda:None)),('input_state',INPUT,inputs)]
for name,kind,callback in callbacks:
 fn=getattr(core,'retro_set_'+name);fn.argtypes=[kind];fn(callback)
core.retro_load_game.argtypes=[C.POINTER(Game)];core.retro_load_game.restype=C.c_bool
core.retro_init()
try:
 assert core.retro_load_game(C.byref(Game(str(HERE/'src/main.lua').encode(),None,0,None)))
 assert frame_time
 def step(n,keys=()):
  buttons.clear();buttons.update(keys)
  for _ in range(n):frame_time(16667);core.retro_run()
  assert not errors,errors
 step(1);assert frame.size==(384,224)
 expected=Image.open(HERE/'src/colors.png').convert('RGB')
 assert frame.crop((20,52,340,148)).tobytes()==expected.tobytes()
 assert len(frame.getcolors(384*224))>16
 # Verify every direction and four action buttons on each port, through pixel indicators.
 for port in range(2):
  for button in [4,5,6,7,0,8,1,9]:
   step(2,[(port,button)])
   actual=frame.getpixel((16+(button+1)*22,185+port*15));expected_color=(235,65,80) if port==0 else (65,155,220)
   assert actual==expected_color,(port,button,actual,expected_color)
   assert frame.getpixel((16+(button+1)*22,185+(1-port)*15))==(0,0,0)
 step(2)
 def marker(color):return min(x for x in range(384) if frame.getpixel((x,165))==color)
 before=[marker((235,65,80)),marker((65,155,220))]
 step(10,[(0,7),(1,6)])
 after=[marker((235,65,80)),marker((65,155,220))]
 assert after==[before[0]+9,before[1]-9],(before,after)
 step(1,[(0,0),(1,8)]);frame.save(HERE/'capture.png')
 for _ in range(600):step(1,[(0,7),(1,6)])
 result=dict(core_commit='a031f95394440022a561ce593d578474ac119c05',resolution=[384,224],png_pixel_identical=True,colors=len(expected.getcolors(320*96)),inputs=16,independent_movement=True,joystick_cache_delay_ticks=1,extra_stability_frames=600,errors=errors,platform='Linux x86-64 only; no Pi/GPIO validation')
 (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
finally:core.retro_unload_game();core.retro_deinit()
