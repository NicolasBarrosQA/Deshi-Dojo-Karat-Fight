"""Seven original short envelopes, in the 2019 66-byte SFX format."""
from pathlib import Path
import json,math
HERE=Path(__file__).resolve().parents[1]
waves=[[0]*32,[round((1-math.cos(2*math.pi*i/32))*7.5) for i in range(32)]]
specs=[
 dict(name='step',note=18,duration=3,volume=4,wave=0,amp=[6,3,0]),
 dict(name='punch',note=30,duration=5,volume=8,wave=0,amp=[4,8,5,2,0]),
 dict(name='kick',note=24,duration=7,volume=8,wave=0,amp=[3,5,8,6,4,2,0]),
 dict(name='block',note=43,duration=5,volume=9,wave=0,amp=[12,8,4,1,0]),
 dict(name='impact',note=20,duration=8,volume=12,wave=0,amp=[15,12,8,5,3,2,1,0]),
 dict(name='point',note=48,duration=12,volume=9,wave=1,amp=[8,7,6,5,5,4,4,3,3,2,1,0],arp=[0]*4+[4]*4+[7]*4),
 dict(name='victory',note=48,duration=24,volume=10,wave=1,amp=[7]*5+[6]*5+[5]*5+[4]*5+[3,2,1,0],arp=[0]*6+[4]*6+[7]*6+[12]*6)
]
encoded=bytearray()
for s in specs:
 for t in range(30):
  vol=s['amp'][t] if t<len(s['amp']) else 0
  arp=s.get('arp',[0]*30)[t] if t<len(s.get('arp',[0]*30)) else 0
  pitch=-min(t,7) if s['wave']==0 else 0
  encoded.extend([15-vol+(s['wave']<<4),arp+((pitch&15)<<4)])
 # Octave3, stereo mute flags both zero in 2019 (one means mute), zero loops.
 encoded.extend([3,0,0,0,0,0])
(HERE/'assets/sfx.bin').write_bytes(encoded)
(HERE/'assets/waves.bin').write_bytes(bytes(v[i]|v[i+1]<<4 for v in waves for i in range(0,32,2)))
(HERE/'assets/audio.json').write_text(json.dumps({'waves':waves,'sounds':specs},separators=(',',':'))+'\n')
print('Original audio:',len(encoded)+32,'bytes;',len(specs),'effects')
