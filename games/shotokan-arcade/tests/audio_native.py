"""Prove seven original envelopes produce unclipped PCM in the old core."""
import ctypes as C
import json,math,struct,sys,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'prototypes/tic80/tools'))
from legacy_core import Core,BATCH
cart=(HERE/'dist/shotokan-arcade.tic').read_bytes();chunks=[];pos=0
while pos<len(cart):
 kind,size,bank=struct.unpack_from('<BHB',cart,pos);data=cart[pos+4:pos+4+size];pos+=4+size
 if kind==5:
  data+=b'''\nlocal original=TIC\nfunction TIC() original();if (G.frame-1)%36==0 then local id=math.floor((G.frame-1)/36);if id<7 then G.sound(id,id%4) end end end\n'''
 chunks.append(struct.pack('<BHB',kind,len(data),bank)+data)
core=Core(ROOT/'.cache/tic80-legacy/tic80_libretro.so',b''.join(chunks));groups=[bytearray() for _ in range(7)];current=0
@BATCH
def audio(data,n):
 groups[current].extend(C.string_at(data,n*4));return n
core.core.retro_set_audio_sample_batch.argtypes=[BATCH];core.core.retro_set_audio_sample_batch(audio)
try:
 for current in range(7):
  for _ in range(36):core.tick()
finally:core.close()
results=[]
for name,data in zip(['step','punch','kick','block','impact','point','victory'],groups):
 values=struct.unpack('<'+'h'*(len(data)//2),data)
 peak=max(abs(v) for v in values);rms=math.sqrt(sum(v*v for v in values)/len(values))
 print(name,peak,rms,flush=True)
 assert 0<peak<32767 and rms>0,(name,peak,rms)
 results.append(dict(effect=name,frames=36,peak=peak,rms=round(rms,2)))
with wave.open(str(HERE/'docs/original-effects.wav'),'wb') as output:
 output.setnchannels(2);output.setsampwidth(2);output.setframerate(44100);output.writeframes(b''.join(groups))
(HERE/'docs/audio-results.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS historical audio: seven audible PCM envelopes, no clipping; WAV captured from core (not microphone)')
