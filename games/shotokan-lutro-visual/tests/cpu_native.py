"""CPU on the actual historical core: fair inputs, matches, profiles and replay parity."""
import hashlib,json,statistics,subprocess,sys,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'tools'))
from native_host import Native
fields='tick x1 x2 energy1 energy2 executed1 executed2 contacts1 contacts2 blocks1 blocks2 chain1 chain2 jumps1 jumps2 wins1 wins2 winner menu choice clock pulses decisions rngLow rngHigh input proof round timer maxChain2 height2'.split()
telemetry='''
local originalDraw=lutro.draw
function lutro.draw()
 originalDraw();local a,b=Scene.players[1],Scene.players[2];local s=Scene.cpu
 local input=0
 for i,k in ipairs({'up','down','left','right','b','y','a'}) do if b.inputs[k] then input=input+2^(i-1) end end
 local data={Scene.tick,math.floor(a.x*16),math.floor(b.x*16),a.energy,b.energy,a.executed,b.executed,a.contacts,b.contacts,a.blocks,b.blocks,a.chain,b.chain,a.jumps,b.jumps,Scene.wins[1],Scene.wins[2],Scene.matchWinner or 0,Scene.menu and 1 or 0,Scene.menuChoice or 0,s.clock,s.pulses,s.decisions,s.rng%65536,math.floor(s.rng/65536),input,Scene.testProof or 0,Scene.round,Scene.timer,b.maxChain,math.floor(b.height*16)}
 for i,v in ipairs(data) do v=math.floor(v);lutro.graphics.setColor(v%256,math.floor(v/256)%256,0);lutro.graphics.rectangle('fill',i,223,1,1) end
end
'''
def fixture(folder,initial=''):
 p=Path(folder);(p/'assets').symlink_to(HERE/'src/assets',target_is_directory=True)
 for name in ('conf.lua','art.lua','techniques.lua','cpu.lua'):(p/name).write_bytes((HERE/'src'/name).read_bytes())
 (p/'main.lua').write_text((HERE/'src/main.lua').read_text()+telemetry+'\nlocal originalLoad=lutro.load\nfunction lutro.load() originalLoad();'+initial+' end\n');return p/'main.lua'
def values(core):return [r+g*256 for r,g,b in [core.frame.getpixel((i,223)) for i in range(1,len(fields)+1)]]
def state(core):return dict(zip(fields,values(core)))
def invariant(s):
 assert 64*16<=s['x1']<=320*16 and 64*16<=s['x2']<=320*16 and abs(s['x2']-s['x1'])>=88*16-1,s
checks=[];matches=[]
# Module contract: delayed observations, no opponent input/queue access, no mutations.
probe='''
local CPU=require('cpu')
local own={x=280,height=0,air=false,face=-1,stun=0,landing=0,blockstun=0,cooldown=0,counter=0}
local foe=setmetatable({x=104,height=0,air=false,phase='KAMAE'},{__index=function(t,k) assert(k~='inputs' and k~='queued' and k~='stun','CPU read private opponent state');return nil end})
for _,level in ipairs({'easy','medium','hard'}) do
 local s=CPU.new(level,1080);local delay=CPU.profiles[level].reaction
 for n=1,delay do assert(next(CPU.update(s,own,foe,false))==nil) end
 local c=CPU.update(s,own,foe,false);assert(c.left and not c.b and not c.a)
 local clock=s.clock;local rng=s.rng;local held=CPU.update(s,own,foe,true)
 assert(clock==s.clock and rng==s.rng and held==c)
 assert(own.x==280 and foe.x==104 and own.action==nil)
 for k,v in pairs(c) do assert(({up=1,down=1,left=1,right=1,b=1,y=1,a=1})[k] and type(v)=='boolean') end
end
Scene.testProof=1234;
'''
with tempfile.TemporaryDirectory() as d:
 with Native(fixture(d,probe)) as core:core.step(1);assert state(core)['proof']==1234,state(core)
checks.append('Real Lua5.1: observation delays22/12/6, ordinary buttons only, no human inputs/queue/stun reads or player mutations, frozen thinking stops')
# A player can finish a whole match with no second port at all.
for level in ('easy','medium','hard'):
 with tempfile.TemporaryDirectory() as d:
  with Native(fixture(d,f'Scene.configure("cpu","{level}");')) as core:
   core.step(1);initial=state(core);assert initial['energy1']==initial['energy2']==100
   for n in range(5000):
    core.step(1);s=state(core);invariant(s)
    if s['winner']:break
   else:raise AssertionError(('No CPU match completion',level,s))
   assert s['winner']==2 and s['wins2']==2,s
   matches.append({'level':level,'ticks_to_two_wins':s['tick'],'last_round_attacks':s['executed2'],'max_chain':s['maxChain2'],'jumps':s['jumps2']})
   core.step(80);assert state(core)['winner']==2
   core.step(2,[(0,3)]);s=state(core);assert s['winner']==0 and s['energy1']==s['energy2']==100 and s['tick']<=1,s
checks.append('Three complete matches against idle P1, no port2 input; each CPU wins two rounds and Start rematches')
# Same fixed human input workload across profiles; collect behavior, not a claimed win rate.
workloads=[];replays=[]
def human_keys(n):
 phase=n%180
 return [(0,7)] if phase<30 else [(0,0)] if phase in (31,32,35,36) else [(0,8)] if phase in (48,49) else [(0,1),(0,4)] if 80<=phase<100 else [(0,4)] if phase in (120,121) else [(0,8)] if phase in (132,133) else []
for level in ('easy','medium','hard'):
 initial=f'Scene.configure("cpu","{level}");Scene.practice=true;Scene.players[1].x=140;Scene.players[2].x=228;'
 frames=[];max_chain=0;contact=0;seen_tech=set()
 with tempfile.TemporaryDirectory() as d:
  with Native(fixture(d,initial)) as core:
   for n in range(900):
    core.step(1,human_keys(n));s=state(core);invariant(s);max_chain=max(max_chain,s['maxChain2'])
    if n<360:frames.append(values(core))
   assert s['energy1']==s['energy2']==100 and s['timer']==3600,s
   assert s['executed2']>0 and max_chain<=({'easy':1,'medium':2,'hard':3}[level]),s
   workloads.append({'level':level,'executed':s['executed2'],'contacts':s['contacts2'],'blocks':s['blocks2'],'max_chain':max_chain,'jumps':s['jumps2']})
 replays.append({'level':level,'initial':initial,'frames':frames,'keys':[human_keys(n) for n in range(360)]})
assert workloads[0]['executed']<workloads[1]['executed']<workloads[2]['executed'],workloads
assert workloads[0]['max_chain']==1 and workloads[1]['max_chain']==2 and workloads[2]['max_chain']==3,workloads
checks.append('Identical900tick human workload: increased CPU attack frequency, one/two/three technique caps, practice unlimited, collision stable')
# A real barrage of circular kicks also exercises anticipatory block and counterplay.
guard_scenario=[]
with tempfile.TemporaryDirectory() as d:
 with Native(fixture(d,'Scene.configure("cpu","hard");Scene.practice=true;Scene.players[1].x=140;Scene.players[2].x=228;')) as core:
  for n in range(1000):
   core.step(1,[(0,7),(0,8)] if n%55 in (0,1) else []);invariant(state(core))
  s=state(core);assert s['blocks2']>0,s
  guard_scenario.append({'level':'hard','cpu_blocks':s['blocks2'],'cpu_contacts':s['contacts2'],'human_contacts':s['contacts1']})
checks.append('Hard CPU actually blocks a physical circular-kick barrage; no perfect guard assumption')
# P2 buttons cannot drive the CPU; deterministic trajectory/RNG must be identical.
sequences=[]
for extra in (False,True):
 with tempfile.TemporaryDirectory() as d:
  with Native(fixture(d,'Scene.configure("cpu","medium");')) as core:
   data=[]
   for n in range(240):
    core.step(1,human_keys(n)+([(1,0),(1,1),(1,8),(1,4),(1,5),(1,6),(1,7)] if extra else []));data.append(values(core))
   sequences.append(data)
assert sequences[0]==sequences[1]
checks.append('Port2 direction/attack/guard buttons do not override or perturb the CPU')
# Arcade menu through both real ports; held direction/Start cannot repeat.
for side in (0,1):
 with tempfile.TemporaryDirectory() as d:
  with Native(fixture(d)) as core:
   core.step(2);core.step(2,[(side,2)]);s=state(core);assert s['menu']==1 and s['choice']==1,s
   before=s['timer'];cpu_clock=s['clock'];core.step(2);core.step(30,[(side,5)]);s=state(core)
   assert s['choice']==2 and s['timer']==before and s['clock']==cpu_clock,s
   core.step(2);core.step(2,[(side,1)]);core.step(2);assert state(core)['menu']==0
   core.step(2,[(side,2)]);core.step(2);assert state(core)['choice']==1
   core.step(2,[(side,5)]);core.step(2);core.step(2,[(side,5)]);assert state(core)['choice']==3
   core.step(2);core.step(14,[(side,3)]);s=state(core);assert s['menu']==0 and s['tick']>=10,s
   # Reopen on hard, choose human port2, then move using real port2.
   core.step(2);core.step(2,[(side,2)]);assert state(core)['choice']==3
   core.step(2);core.step(2,[(side,5)]);core.step(2);core.step(2,[(side,0)]);core.step(2)
   before=state(core)['x2'];core.step(12,[(1,6)]);assert state(core)['x2']<before
checks.append('Select/menu on both ports: directions choose, held direction single step, freeze fight/CPU, defense cancels, hard confirmed, held Start single reset, human2 restored')
# Pixel and AI replay agreement across interpreters, including the portable PRNG.
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'replays.json';p.write_text(json.dumps({'fields':fields,'replays':replays}));subprocess.run(['node',str(HERE/'tests/cpu_replay.cjs'),str(p)],check=True,timeout=120)
checks.append('1080 per-tick CPU replays: native Lua5.1 vs offline Fengari match positions, energy, inputs, decisions and RNG exactly after quantization')
# Measure actual CPU+simulation/draw on x86 only.
times=[]
with tempfile.TemporaryDirectory() as d:
 with Native(fixture(d,'Scene.configure("cpu","hard");Scene.practice=true;'),capture=False) as core:
  for n in range(1800):
   t=time.perf_counter();core.step(1,human_keys(n));times.append((time.perf_counter()-t)*1000)
result={'passed':len(checks),'checks':checks,'matches':matches,'workload':workloads,'guard_scenario':guard_scenario,'replay_ticks':1080,'artifact_sha256':hashlib.sha256((HERE/'dist/deshi-dojo-visual.lutro').read_bytes()).hexdigest(),'native_cpu_frames_measured':len(times),'mean_ms':statistics.mean(times),'p95_ms':sorted(times)[1709],'limitations':'Synthetic player/idle opponents validate behavior, not human difficulty ratings or Pi/GPIO/performance. Belt colors identify CPU profiles in HUD; character art unchanged.'}
(HERE/'docs/cpu-native-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
