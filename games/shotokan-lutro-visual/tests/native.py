"""Real Lua 5.1/core inputs, collision invariants and arcade/technique event separation."""
import hashlib,json,statistics,sys,tempfile,time
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'tools'))
from native_host import Native
catalog=json.loads((HERE/'assets/techniques.json').read_text());tech=catalog['techniques']
fields='tick x1 x2 pose1 pose2 points1 points2 contacts1 contacts2 freeze blocks1 blocks2 parries1 parries2 h1 h2 air1 air2 chain1 chain2 executed1 executed2 jumps1 jumps2 maxChain1 maxChain2 age1 age2 queued1 queued2 energy1 energy2 stun1 stun2 combo1 combo2 timer wins1 wins2 result winner zone blocked parry counter airborne hook'.split()
telemetry='''
local originalDraw=lutro.draw
function lutro.draw()
 originalDraw()
 local a,b=Scene.players[1],Scene.players[2];local e=Scene.lastContact or {}
 local data={Scene.tick,a.x,b.x,a.pose,b.pose,a.points,b.points,a.contacts,b.contacts,Scene.freeze,a.blocks,b.blocks,a.parries,b.parries,a.height,b.height,a.air and 1 or 0,b.air and 1 or 0,a.chain,b.chain,a.executed,b.executed,a.jumps,b.jumps,a.maxChain,b.maxChain,a.action and a.action.age or 0,b.action and b.action.age or 0,a.queued and 1 or 0,b.queued and 1 or 0,a.energy,b.energy,a.stun,b.stun,a.comboHits,b.comboHits,Scene.timer,Scene.wins[1],Scene.wins[2],Scene.result and Scene.result+1 or 0,Scene.matchWinner or 0,({jodan=1,chudan=2,gedan=3})[e.zone] or 0,e.blocked and 1 or 0,e.parry and 1 or 0,e.counter and 1 or 0,e.airborne and 1 or 0,Scene.testHook or 0}
 for i,v in ipairs(data) do v=math.floor(v);lutro.graphics.setColor(v%256,math.floor(v/256)%256,0);lutro.graphics.rectangle('fill',i,223,1,1) end
end
'''
def fixture(parent,initial=''):
 p=Path(parent);(p/'assets').symlink_to(HERE/'src/assets',target_is_directory=True)
 for name in ('conf.lua','art.lua','techniques.lua','cpu.lua'):(p/name).write_bytes((HERE/'src'/name).read_bytes())
 (p/'main.lua').write_text((HERE/'src/main.lua').read_text()+telemetry+'\nlocal originalLoad=lutro.load\nfunction lutro.load() originalLoad();Scene.configure("versus","easy");'+initial+' end\n')
 return p/'main.lua'
def state(core):
 return dict(zip(fields,[r+g*256 for r,g,b in [core.frame.getpixel((i,223)) for i in range(1,len(fields)+1)]]))
def controls(id,side=0,face=1):
 t=tech[id];keys=[(side,{'defense':1,'punch':0,'kick':8}[t['button']])]
 for m in t['direction'].split('_'):
  d={'up':4,'down':5,'forward':7 if face==1 else 6,'back':6 if face==1 else 7}.get(m)
  if d is not None:keys.append((side,d))
 return keys
def invariant(s,left=1):
 assert 64<=s['x1']<=320 and 64<=s['x2']<=320 and s[f'x{3-left}']-s[f'x{left}']>=87,(left,s)
near='Scene.players[1].x=140;Scene.players[2].x=228;'
checks=[]
with Native(HERE/'dist/deshi-dojo-visual.lutro') as core:
 core.step(1);assert core.resolution==(384,224);core.frame.save(HERE/'docs/scene-native.png')
 stage=Image.open(HERE/'src/assets/dojo.png').convert('RGB')
 assert core.frame.crop((0,40,25,195)).tobytes()==stage.crop((0,40,25,195)).tobytes()
 assert len(core.frame.getcolors(384*224))>1000
 core.step(600,[(0,7),(1,6)])
checks.append('Delivered cart without telemetry: historical loader/PNGs, 384x224, 600 movement ticks')
# Frame-by-frame barrier, both sides, stationary target, walls, jumps and hostile large proposals.
collision_ticks=0
for left in (1,2):
 with tempfile.TemporaryDirectory() as d:
  initial='' if left==1 else 'Scene.players[1].x=280;Scene.players[2].x=104;Scene.left=2;'
  with Native(fixture(d,initial)) as core:
   core.step(2);before=state(core)
   inward=[(left-1,7),(2-left,6)]
   for n in range(200):
    core.step(1,inward);invariant(state(core),left);collision_ticks+=1
   assert state(core)[f'x{left}']>before[f'x{left}']
   stationary=state(core)[f'x{3-left}']
   for n in range(80):
    core.step(1,[(left-1,7)]);s=state(core);invariant(s,left);collision_ticks+=1
    assert s[f'x{3-left}']==stationary,s
   core.step(2)
   for n in range(60):
    keys=inward+[(left-1,4)] if n<2 else inward+controls('mawashi',left-1,1) if n in (12,13) else inward
    core.step(1,keys);invariant(state(core),left);collision_ticks+=1
 for wall in (64,232):
  with tempfile.TemporaryDirectory() as d:
   initial=f'Scene.players[{left}].x={wall};Scene.players[{3-left}].x={wall+88};Scene.left={left};'
   # Pre-movement order is supplied before a full crossing attempt.
   initial+=f'local old={{{wall if left==1 else wall+88},{wall+88 if left==1 else wall}}};Scene.players[{left}].x=310;Scene.players[{3-left}].x=70;Scene.resolveBodies({left},old);'
   with Native(fixture(d,initial)) as core:
    core.step(1);invariant(state(core),left)
checks.append(f'{collision_ticks} per-tick collision checks: no crossing, stationary opponent, both orientations, jumps, corners and extreme crossing proposals')
pose_cases=0
for side in (0,1):
 for face in (1,-1):
  for id in catalog['order']:
   t=tech[id]
   initial=f'Scene.players[{side+1}].x={104 if face==1 else 280};Scene.players[{2-side}].x={280 if face==1 else 104};'
   with tempfile.TemporaryDirectory() as d:
    with Native(fixture(d,initial)) as core:
     core.step(2)
     if t.get('air'):core.step(2,[(side,4)]);core.step(8)
     seen=set();keys=controls(id,side,face)
     for n in range(48):
      core.step(1,keys if t['kind']=='defense' or n<2 else []);seen.add(state(core)[f'pose{side+1}'])
     assert set(t['poses']).issubset(seen),(id,side,face,seen)
   pose_cases+=1
checks.append(f'{pose_cases} active technique/port/facing cases: all authored poses reached by real buttons')
matrix=[]
for attack in [id for id in catalog['order'] if tech[id]['kind']=='attack' and not tech[id].get('air')]:
 for defense in ('kamae','age','gedan','soto','uchi'):
  # Start at the barrier after coverage is formed; short backwards movement still matters.
  with tempfile.TemporaryDirectory() as d:
   with Native(fixture(d,'Scene.players[1].x=232;Scene.players[2].x=320;')) as core:
    guard=controls(defense,1,-1);core.step(8,guard)
    core.step(2,guard+controls(attack));core.step(36,guard);s=state(core)
    zone={1:'jodan',2:'chudan',3:'gedan'}.get(s['zone']);blocked=zone==tech[defense]['zone']
    assert s['contacts1']==1 and s['points1']==int(not blocked) and s['blocks2']==int(blocked),(attack,defense,s)
    assert zone is not None,(attack,defense,s)
    assert s['energy2']==100-(0 if blocked else tech[attack]['damage']),s
    matrix.append({'attack':attack,'defense':defense,'nominal_zone':tech[attack]['zone'],'contact_zone':zone,'blocked':blocked})
checks.append(f'{len(matrix)} ground attack/defense pairs: real contact heights, energy loss only on unblocked hits')
for side in (0,1):
 with tempfile.TemporaryDirectory() as d:
  with Native(fixture(d,near)) as core:
   core.step(2);core.step(80,[(side,0)]);s=state(core)
   assert s[f'executed{side+1}']==1 and s[f'contacts{side+1}']==1,s
   core.step(2);core.step(2,[(side,0)]);core.step(32)
   assert state(core)[f'executed{side+1}']==2,state(core)
checks.append('Held punch on both ports strikes once; a new press is accepted')
with tempfile.TemporaryDirectory() as d:
 with Native(fixture(d,near)) as core:
  core.step(2);core.step(2,[(0,0),(1,0)]);core.step(24);s=state(core)
  assert s['contacts1']==s['contacts2']==1 and s['energy1']==s['energy2']==94,s
checks.append('Simultaneous contacts resolve from the same frame before either stun')
with tempfile.TemporaryDirectory() as d:
 with Native(fixture(d)) as core:
  core.step(2);core.step(2,controls('mawashi'));core.step(30);assert state(core)['contacts1']==0
checks.append('Out-of-range kick misses')
# Timely guard, immediate counter from held guard, and late preparation.
with tempfile.TemporaryDirectory() as d:
 with Native(fixture(d,near)) as core:
  core.step(2);guard=controls('soto',1,-1)
  core.step(2,guard+controls('gyaku'));core.step(4,guard);s=state(core)
  assert s['blocked']==s['parry']==1,s
  core.step(2,guard+[(1,0)]);core.step(18);s=state(core)
  assert s['contacts2']==1 and s['counter']==1,s
checks.append('Timed soto reception; fresh punch from held guard buffered through blockstun and tagged counter')
with tempfile.TemporaryDirectory() as d:
 with Native(fixture(d,near)) as core:
  core.step(2);core.step(2,controls('gyaku'));core.step(2)
  core.step(2,controls('soto',1,-1));core.step(20);s=state(core)
  assert s['points1']==1 and s['blocks2']==0,s
checks.append('Late defense cannot protect during preparation')
for side in (0,1):
 with tempfile.TemporaryDirectory() as d:
  with Native(fixture(d)) as core:
   core.step(2);core.step(80,[(side,4)]);s=state(core)
   assert s[f'jumps{side+1}']==1 and s[f'h{side+1}']==s[f'air{side+1}']==0,s
   core.step(2);core.step(2,[(side,4)]);core.step(12);assert state(core)[f'h{side+1}']>20
 for id in ('age','jodan'):
  with tempfile.TemporaryDirectory() as d:
   with Native(fixture(d)) as core:
    core.step(2);core.step(20,controls(id,side,1 if side==0 else -1));assert state(core)[f'jumps{side+1}']==0
checks.append('Jump/landing on both ports, no held-up autojump, up+attack/defense remains grounded')
with tempfile.TemporaryDirectory() as d:
 with Native(fixture(d)) as core:
  core.step(2);core.step(2,[(0,4)]);core.step(12,controls('age'));s=state(core)
  assert s['jumps1']==s['air1']==0 and s['pose1']==15,s
checks.append('Defense replaces grounded takeoff before launch')
with tempfile.TemporaryDirectory() as d:
 with Native(fixture(d,near)) as core:
  core.step(8,[(1,5)]);assert state(core)['pose2']==90
  core.step(2,[(1,5)]+controls('jodan'));core.step(25,[(1,5)]);assert state(core)['contacts1']==0,state(core)
checks.append('Planted low stance lowers hurt regions; high punch passes above')
air_matrix=[]
for attack in ('tobi_mae','air_tsuki'):
 for defense in ('kamae','age','gedan','soto','uchi'):
  with tempfile.TemporaryDirectory() as d:
   with Native(fixture(d,'Scene.players[1].x=232;Scene.players[2].x=320;')) as core:
    guard=controls(defense,1,-1);core.step(8,guard)
    core.step(2,guard+[(0,4)]);core.step(8,guard)
    core.step(2,guard+controls(attack));core.step(46,guard);s=state(core)
    zone={1:'jodan',2:'chudan',3:'gedan'}.get(s['zone']);blocked=zone==tech[defense]['zone']
    assert s['contacts1']==s['airborne']==1 and zone is not None,(attack,defense,s)
    assert s['points1']==int(not blocked) and s['blocks2']==int(blocked),(attack,defense,s)
    assert s['h1']==s['air1']==0 and s['executed1']==1,s
    air_matrix.append({'attack':attack,'defense':defense,'contact_zone':zone,'blocked':blocked})
checks.append('10 aerial/defense pairs: actual height, one strike per jump, landing')
# Actual beginner sequence, early inputs, contact count not merely execution count.
combo_cases=0
for side in (0,1):
 for face in (1,-1):
  with tempfile.TemporaryDirectory() as d:
   initial=f'Scene.players[{side+1}].x={140 if face==1 else 228};Scene.players[{2-side}].x={228 if face==1 else 140};'
   with Native(fixture(d,initial)) as core:
    core.step(2);core.step(2,[(side,0)]);core.step(1)
    core.step(2,[(side,0)]) # Early second press must survive first impact/retraction.
    for n in range(25):
     s=state(core)
     if s[f'executed{side+1}']==2:break
     core.step(1)
    else:raise AssertionError(('Second input lost',state(core)))
    core.step(1);core.step(2,[(side,8)])
    best=0
    for n in range(32):
     core.step(1,[(side,8)]);s=state(core);best=max(best,s[f'combo{side+1}']);invariant(s,1 if side==0 and face==1 or side==1 and face==-1 else 2)
    assert s[f'executed{side+1}']==3 and s[f'contacts{side+1}']==3 and best==3,(side,face,s,best)
    assert s[f'energy{2-side}']==70,s
    core.step(40,[(side,8)]);assert state(core)[f'executed{side+1}']==3,state(core)
    combo_cases+=1
checks.append('Soco > soco > chute: four port/facing cases, early buffer, three actual hits, real combo count, no held-button repetition')
# Incoming stun/hitstop cannot eat a fresh defender command.
with tempfile.TemporaryDirectory() as d:
 with Native(fixture(d,near)) as core:
  core.step(2);core.step(2,[(0,0)]);core.step(3);s=state(core)
  assert s['stun2']>0 and s['pose2']==85 and s['freeze']>0,s
  before=s['x2'];core.step(2,[(1,0)]);core.step(28);s=state(core)
  assert s['executed2']==1 and s['contacts2']==1 and s['x2']>before,s
checks.append('Chest recoil pose, physical knockback and defender input retained through hitstop/stun')
# Technical event observer remains independent of arcade HP and rounds.
hook="Scene.onContact=function(e) assert(e.technique and e.distance>=88 and e.overlap>0 and e.tick>0 and e.quality=='arcade');Scene.testHook=(Scene.testHook or 0)+1 end;"
for practice in (False,True):
 with tempfile.TemporaryDirectory() as d:
  with Native(fixture(d,near+hook+('Scene.practice=true;' if practice else ''))) as core:
   core.step(2);core.step(2,[(0,0)]);core.step(20);s=state(core)
   assert s['hook']==1 and s['energy2']==(100 if practice else 94),s
   assert (s['timer']==3600)==practice,s
checks.append('Technical contact hook records geometry independently; practice disables energy/time loss')
# Deterministic round decisions and best of three, no external services.
for winner in (0,1,2):
 with tempfile.TemporaryDirectory() as d:
  initial=f'Scene.timer=1;Scene.players[1].energy={80 if winner==1 else 60};Scene.players[2].energy={80 if winner==2 else 60};Scene.wins={{1,1}};'
  with Native(fixture(d,initial)) as core:
   core.step(1);s=state(core);assert s['result']==winner+1 and s['winner']==winner,s
   if winner:core.step(110);assert state(core)['winner']==winner
   else:core.step(96);assert state(core)['timer']==3599 and state(core)['result']==0 and state(core)['energy1']==state(core)['energy2']==100
checks.append('Timeout energy comparison, draw, automatic next round and two-win match end')
with tempfile.TemporaryDirectory() as d:
 with Native(fixture(d,near+'Scene.players[2].energy=6;')) as core:
  core.step(2);core.step(2,[(0,0)]);core.step(8);s=state(core)
  assert s['energy2']==0 and s['result']==2 and s['wins1']==1,s
checks.append('KO closes round and awards winner')
with tempfile.TemporaryDirectory() as d:
 with Native(fixture(d)) as core:
  core.step(2);core.step(14,[(0,3)]);assert state(core)['tick']>=10
  core.step(2);core.step(2,[(1,3)]);assert state(core)['tick']<=1
checks.append('Start on either port resets once per fresh press')
times=[]
with Native(HERE/'dist/deshi-dojo-visual.lutro',capture=False) as core:
 core.step(60)
 for n in range(1800):
  keys=[(0,7),(1,6)] if n%180<35 else [(0,0)] if n%180 in (40,41,44,45) else [(0,8)] if n%180 in (56,57) else [(1,4)] if n%180 in (100,101) else [(1,8)] if n%180 in (110,111) else []
  t=time.perf_counter();core.step(1,keys);times.append((time.perf_counter()-t)*1000)
result={'passed':len(checks),'checks':checks,'technique_input_cases':pose_cases,'zone_matrix':matrix,'air_zone_matrix':air_matrix,'combo_cases':combo_cases,'collision_ticks':collision_ticks,
 'core_commit':'a031f95394440022a561ce593d578474ac119c05','artifact_sha256':hashlib.sha256((HERE/'dist/deshi-dojo-visual.lutro').read_bytes()).hexdigest(),
 'native_frames_measured':len(times),'mean_ms':statistics.mean(times),'p95_ms':sorted(times)[1709],'p99_ms':sorted(times)[1781],'max_ms':max(times),'above_16_67_ms':sum(t>16.67 for t in times),
 'limitations':'Linux x86-64 only; game feel, Pi/ARM/GPIO/real monitor/instructor review pending'}
(HERE/'docs/native-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('zone_matrix','air_zone_matrix')},indent=2))
