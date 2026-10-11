"""Minimal desktop-only host for the pinned historical Lutro libretro core."""
import ctypes as C
import sys,time,tempfile,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'prototypes/tic80/tools'))
from legacy_core import ENV,VIDEO,LOG,BATCH,AUDIO,POLL,INPUT,Game
CORE=ROOT/'.cache/lutro-research/source/lutro_libretro.so'
TIMER=C.CFUNCTYPE(C.c_int64);FRAME=C.CFUNCTYPE(None,C.c_int64)
class Perf(C.Structure):
 _fields_=[('clock',C.c_void_p)]+[(name,C.c_void_p) for name in ['features','counter','register','start','stop','log']]
class Native:
 def __init__(self,path,capture=True):
  self.workspace=tempfile.TemporaryDirectory(prefix='dojo-lutro-host-')
  path=Path(path).resolve()
  if path.suffix=='.lutro':
   # The historical loader extracts next to the archive; isolate that write.
   target=Path(self.workspace.name)/path.name;shutil.copyfile(path,target);path=target
  # This revision retains framebuffer/canvas globals after retro_deinit.
  # Fresh library image per host models a fresh core load, without patching it.
  library=Path(self.workspace.name)/'lutro_libretro.so';shutil.copyfile(CORE,library)
  self.core=C.CDLL(str(library))
  self.buttons=set();self.errors=[];self.frame=None;self.frame_time=None;self.capture=capture
  self.clock=TIMER(lambda:time.monotonic_ns()//1000)
  @LOG
  def logger(level,message):
   if level>=3:self.errors.append(message.decode(errors='replace'))
  @ENV
  def env(command,data):
   if command==27:C.cast(data,C.POINTER(C.c_void_p))[0]=C.cast(logger,C.c_void_p).value;return True
   if command==28:C.cast(data,C.POINTER(Perf))[0]=Perf(C.cast(self.clock,C.c_void_p).value,None,None,None,None,None,None);return True
   if command==10:return C.cast(data,C.POINTER(C.c_int))[0]==1
   if command==21:self.frame_time=FRAME(C.cast(data,C.POINTER(C.c_void_p))[0]);return True
   return False
  @VIDEO
  def video(data,w,h,pitch):
   self.resolution=(w,h)
   if self.capture:
    self.frame=Image.frombytes('RGB',(w,h),C.string_at(data,pitch*h),'raw','BGRX',pitch)
  @INPUT
  def inputs(port,device,index,key):return int(device==1 and (port,key) in self.buttons)
  self.callbacks=[('environment',ENV,env),('video_refresh',VIDEO,video),('audio_sample',AUDIO,AUDIO(lambda l,r:None)),
   ('audio_sample_batch',BATCH,BATCH(lambda data,n:n)),('input_poll',POLL,POLL(lambda:None)),('input_state',INPUT,inputs)]
  for name,kind,callback in self.callbacks:
   fn=getattr(self.core,'retro_set_'+name);fn.argtypes=[kind];fn(callback)
  self.core.retro_load_game.argtypes=[C.POINTER(Game)];self.core.retro_load_game.restype=C.c_bool
  self.core.retro_init()
  assert self.core.retro_load_game(C.byref(Game(str(Path(path).resolve()).encode(),None,0,None))),self.errors
  assert self.frame_time,'Historical frame-time callback missing'
 def step(self,n=1,keys=()):
  self.buttons.clear();self.buttons.update(keys)
  for _ in range(n):self.frame_time(16667);self.core.retro_run()
  assert not self.errors,self.errors
 def close(self):
  self.core.retro_unload_game();self.core.retro_deinit()
  if self.workspace:self.workspace.cleanup()
 def __enter__(self):return self
 def __exit__(self,*args):self.close()
