"""Screenshots and continuous four-technique GIF, delivered cart without telemetry."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'prototypes/tic80/tools'))
from legacy_core import Core
cart=(HERE/'dist/shotokan-arcade.tic').read_bytes()
def open_core():return Core(ROOT/'.cache/tic80-legacy/tic80_libretro.so',cart)
def step(core,n,keys=(),film=None):
 core.buttons.clear()
 for key in keys:core.key(key,True)
 for i in range(n):
  core.tick()
  if film is not None and i%3==0:
   w,h,rgb=core.frame
   film.append(Image.frombytes('RGB',(w,h),rgb).resize((768,432),Image.Resampling.NEAREST))
def capture(core,name):
 path=HERE/'docs'/f'{name}.png';path.write_bytes(core.png())
 Image.open(path).resize((960,544),Image.Resampling.NEAREST).save(HERE/'docs'/f'{name}-4x.png')
def start(core):
 step(core,1,(4,));step(core,1);step(core,1,(4,12));step(core,36)
core=open_core()
step(core,1);capture(core,'title')
step(core,1,(4,));step(core,1);capture(core,'selection')
step(core,1,(4,12));step(core,1);capture(core,'hajime')
step(core,35);capture(core,'kumite')
step(core,45,(3,10));capture(core,'movement')
step(core,60,(4,5));step(core,1);capture(core,'diagnostic');core.close()
for index,name in enumerate(['oi-zuki','gyaku-zuki','mae-geri','mawashi-geri']):
 core=open_core();step(core,1);start(core);step(core,50,(3,10))
 step(core,1,(4+index,));step(core,[9,7,13,16][index]);capture(core,name);core.close()
core=open_core();step(core,1);start(core)
step(core,54,(3,10));step(core,1,(5,11));step(core,7,(11,));capture(core,'block');core.close()
core=open_core();step(core,1);start(core)
for _ in range(3):
 step(core,50,(3,10));step(core,1,(6,));step(core,13);step(core,60)
capture(core,'result')
step(core,1,(4,));step(core,36);capture(core,'rematch');core.close()
# Actual continuous fight: 3-3 after P1 oi, P2 gyaku, P1 mae, P2 mawashi.
core=open_core();step(core,1);start(core);film=[]
for n,keys in [(48,()),(18,(3,10)),(12,(2,11)),(42,(3,10)),
 (1,(4,)),(9,()),(65,()),(50,(3,10)),(1,(13,)),(7,()),(65,()),
 (50,(3,10)),(1,(6,)),(13,()),(65,()),(50,(3,10)),(1,(15,)),(16,()),(65,())]:step(core,n,keys,film)
film[0].save(HERE/'docs/kumite-execution.gif',save_all=True,append_images=film[1:],duration=50,loop=0,optimize=True)
core.close()
# Comparison uses real old/new captures; labels are outside the gameplay pixels.
import zipfile
with zipfile.ZipFile(ROOT/'archives/shotokan-arcade-v01.zip') as z:
 import io
 before=Image.open(io.BytesIO(z.read('docs/mae-geri-4x.png'))).convert('RGB')
after=Image.open(HERE/'docs/mae-geri-4x.png').convert('RGB')
comparison=Image.new('RGB',(1920,570),'#11141f');comparison.paste(before,(0,26));comparison.paste(after,(960,26))
d=ImageDraw.Draw(comparison);d.text((15,8),'V01 - CAPTURA REAL',fill='#faf4e7');d.text((975,8),'V02 - CAPTURA REAL',fill='#faf4e7')
comparison.save(HERE/'docs/comparison.png')
print('PASS delivered cartridge: 13 native views, continuous movement/four-technique GIF and real v01/v02 comparison')
