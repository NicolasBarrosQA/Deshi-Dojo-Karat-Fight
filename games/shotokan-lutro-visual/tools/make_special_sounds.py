"""Original short dry arcade foley, PCM16 mono 44100, canonical 44-byte WAV."""
from pathlib import Path
import math,random,struct,wave
out=Path(__file__).resolve().parents[1]/'src/assets'
for name,frames,frequency,noise,decay in [('sweep',11,180,.7,7),('ground',14,65,.45,12),('finish',8,110,.25,18)]:
 rng=random.Random(1703);n=735*frames;samples=[];smooth=0
 for i in range(n):
  t=i/44100;smooth=smooth*.82+rng.uniform(-1,1)*.18
  value=(smooth*noise+math.sin(2*math.pi*frequency*t)*(1-noise))*math.exp(-t*decay)*.32
  samples.append(round(value*32767))
 with wave.open(str(out/('special-'+name+'.wav')),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(44100);f.writeframes(struct.pack('<'+'h'*n,*samples))
