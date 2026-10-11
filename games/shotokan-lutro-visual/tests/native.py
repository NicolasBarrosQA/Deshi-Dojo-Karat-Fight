"""Exercise real Lua 5.1/historical core with temporary pixel telemetry only."""
import hashlib,json,statistics,sys,tempfile,time
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'tools'))
from native_host import Native
tech=json.loads((HERE/'assets/techniques.json').read_text())['techniques']
telemetry='''
local originalDraw=lutro.draw
function lutro.draw()
 originalDraw()
 local a,b=Scene.players[1],Scene.players[2]
 local e=Scene.lastContact or {}
 local data={Scene.tick,a.x,b.x,a.pose,b.pose,a.points,b.points,a.contacts,b.contacts,Scene.freeze,a.age,b.age,a.blocks,b.blocks,a.parries,b.parries,e.blocked and 1 or 0,e.parry and 1 or 0,e.counter and 1 or 0}
 for i,v in ipairs(data) do
  v=math.floor(v);lutro.graphics.setColor(v%256,math.floor(v/256)%256,0)
  lutro.graphics.rectangle('fill',i,223,1,1)
 end
end
'''
def fixture(parent,initial=''):
 p=Path(parent);(p/'assets').symlink_to(HERE/'src/assets',target_is_directory=True)
 for name in ('conf.lua','art.lua','techniques.lua'):(p/name).write_bytes((HERE/'src'/name).read_bytes())
 (p/'main.lua').write_text((HERE/'src/main.lua').read_text()+telemetry+'''
local originalLoad=lutro.load
function lutro.load() originalLoad() '''+initial+''' end
''')
 return p/'main.lua'
def state(core):
 return [r+g*256 for r,g,b in [core.frame.getpixel((i,223)) for i in range(1,20)]]
def controls(id,side=0,face=1):
 action=1 if tech[id]['kind']=='defense' else 0 if id in ('gyaku','oi','jodan') else 8
 keys=[(side,action)]
 modifier={'age':4,'gedan':5,'soto':7 if face==1 else 6,'uchi':6 if face==1 else 7,
 'oi':7 if face==1 else 6,'jodan':4,'mae_low':5,'mawashi':7 if face==1 else 6}.get(id)
 if modifier is not None:keys.append((side,modifier))
 return keys
checks=[]
with Native(HERE/'dist/deshi-dojo-visual.lutro') as core:
 core.step(1);assert core.resolution==(384,224)
 core.frame.save(HERE/'docs/scene-native.png')
 stage=Image.open(HERE/'src/assets/dojo.png').convert('RGB')
 assert core.frame.crop((0,40,25,195)).tobytes()==stage.crop((0,40,25,195)).tobytes()
 assert len(core.frame.getcolors(384*224))>1000
 core.step(600,[(0,7),(1,6)])
checks.append('Delivered uninstrumented .lutro loads/renders historical PNGs, 384x224; 600 movement frames')
with tempfile.TemporaryDirectory(prefix='dojo-input-') as d:
 with Native(fixture(d)) as core:
  core.step(2);before=state(core)
  core.step(14,[(0,7),(1,6)]);after=state(core)
  assert after[1]>before[1] and after[2]<before[2],(before,after)
  core.step(230,[(0,7),(1,6)]);s=state(core);assert s[2]-s[1]>=58,s
checks.append('Two independent ports, body separation, stage limits')
# Every technique on both ports and both facing directions, via physical buttons.
pose_cases=0
for side in (0,1):
 for face in (1,-1):
  for id,t in tech.items():
   if id=='kamae':continue
   initial='Scene.players[%d].x=%d;Scene.players[%d].x=%d'%(side+1,104 if face==1 else 280,2-side,280 if face==1 else 104)
   with tempfile.TemporaryDirectory(prefix='dojo-poses-') as d:
    with Native(fixture(d,initial)) as core:
     core.step(2);keys=controls(id,side,face);seen=set()
     for n in range(48):
      core.step(1,keys if t['kind']=='defense' or n<2 else [])
      seen.add(state(core)[3+side])
     assert set(t['poses']).issubset(seen),(id,side,face,seen)
   pose_cases+=1
checks.append('40 technique/port/facing cases: all authored poses reached by commands')
# Zone matrix: all six attacks vs four named blocks + neutral middle guard.
matrix=[]
for attack in ('gyaku','oi','jodan','mae','mae_low','mawashi'):
 for defense in ('kamae','age','gedan','soto','uchi'):
  with tempfile.TemporaryDirectory(prefix='dojo-zones-') as d:
   with Native(fixture(d,'Scene.players[1].x=150;Scene.players[2].x=217')) as core:
    guard=controls(defense,1,-1);core.step(24,guard)
    core.step(2,guard+controls(attack));core.step(58,guard)
    s=state(core);blocked=tech[attack]['zone']==tech[defense]['zone']
    assert s[7]==1 and s[5]==(0 if blocked else 1) and s[13]==int(blocked),(attack,defense,s)
    matrix.append({'attack':attack,'defense':defense,'blocked':blocked})
checks.append('30 attack/defense pairs: correct zone blocks; wrong zones are vulnerable')
with tempfile.TemporaryDirectory(prefix='dojo-edge-') as d:
 with Native(fixture(d,'Scene.players[1].x=150;Scene.players[2].x=217')) as core:
  core.step(2);core.step(90,controls('gyaku'));assert state(core)[5:9]==[1,0,1,0],state(core)
  core.step(2);core.step(80,controls('gyaku'));assert state(core)[7]==2,state(core)
checks.append('Held attack button cannot repeat; release/fresh press works')
with tempfile.TemporaryDirectory(prefix='dojo-trade-') as d:
 with Native(fixture(d,'Scene.players[1].x=150;Scene.players[2].x=217')) as core:
  core.step(2);core.step(2,controls('gyaku')+controls('gyaku',1,-1));core.step(42)
  assert state(core)[5:9]==[1,1,1,1],state(core)
checks.append('Simultaneous contacts evaluate both fighters before stun')
with tempfile.TemporaryDirectory(prefix='dojo-distance-') as d:
 with Native(fixture(d)) as core:
  core.step(2);core.step(2,controls('mawashi'));core.step(48)
  assert state(core)[5:9]==[0,0,0,0],state(core)
checks.append('Out-of-range kick misses')
# Start soto as punch age reaches 5: defence reaches age 9 at first contact.
with tempfile.TemporaryDirectory(prefix='dojo-timing-') as d:
 with Native(fixture(d,'Scene.players[1].x=150;Scene.players[2].x=217')) as core:
  core.step(2);core.step(2,controls('gyaku'));core.step(2)
  core.step(2,controls('soto',1,-1));core.step(12,controls('soto',1,-1));s=state(core)
  assert s[5]==0 and s[15]==1 and s[17]==1,s
  core.step(2,controls('soto',1,-1))
  # Fresh punch with guard released uses the parry counter window.
  core.step(2,controls('gyaku',1,-1));core.step(34)
  s=state(core);assert s[6]==1 and s[18]==1,s
checks.append('Early coverage receives on time and enables tagged counterattack')
# Late block is still in preparation when the fist contacts.
with tempfile.TemporaryDirectory(prefix='dojo-late-') as d:
 with Native(fixture(d,'Scene.players[1].x=150;Scene.players[2].x=217')) as core:
  core.step(2);core.step(2,controls('gyaku'));core.step(7)
  core.step(2,controls('soto',1,-1));core.step(30,controls('soto',1,-1))
  s=state(core);assert s[5]==1 and s[13]==0,s
checks.append('Late defence does not protect during its preparation')
with tempfile.TemporaryDirectory(prefix='dojo-switch-') as d:
 with Native(fixture(d)) as core:
  core.step(24,controls('age'));core.step(2,controls('gedan'));assert state(core)[3]==16,state(core)
  core.step(12,controls('gedan'));assert state(core)[3]==18,state(core)
checks.append('Held defence direction change starts a fresh technique preparation')
times=[]
with Native(HERE/'dist/deshi-dojo-visual.lutro',capture=False) as core:
 core.step(60)
 for n in range(1800):
  keys=[(0,7),(1,6)] if n%240<100 else controls('mae') if n%240==130 else []
  t=time.perf_counter();core.step(1,keys);times.append((time.perf_counter()-t)*1000)
result={'passed':len(checks),'checks':checks,'technique_input_cases':pose_cases,'zone_matrix':matrix,
 'core_commit':'a031f95394440022a561ce593d578474ac119c05',
 'artifact_sha256':hashlib.sha256((HERE/'dist/deshi-dojo-visual.lutro').read_bytes()).hexdigest(),
 'native_frames_measured':len(times),'mean_ms':statistics.mean(times),'p95_ms':sorted(times)[1709],
 'p99_ms':sorted(times)[1781],'max_ms':max(times),'above_16_67_ms':sum(t>16.67 for t in times),
 'limitations':'Linux x86-64 only; Pi/ARM/GPIO/real monitor/instructor review pending'}
(HERE/'docs/native-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='zone_matrix'},indent=2))
