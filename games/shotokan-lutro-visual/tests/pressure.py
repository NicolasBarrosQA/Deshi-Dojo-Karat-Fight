"""Reproduce punch-only pressure through real buttons on the historical Lua core."""
import hashlib,json,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'tools'))
from native_host import Native
FIELDS='tick energy1 energy2 points1 points2 blocks2 combo1 winner wins1 wins2 result'.split()
TELEMETRY='''
local originalDraw=lutro.draw
function lutro.draw()
 originalDraw();local a,b=Scene.players[1],Scene.players[2]
 local data={Scene.tick,a.energy,b.energy,a.points,b.points,b.blocks,a.comboHits,Scene.matchWinner or 0,Scene.wins[1],Scene.wins[2],Scene.result and Scene.result+1 or 0}
 for i,v in ipairs(data) do v=math.floor(v);lutro.graphics.setColor(v%256,math.floor(v/256)%256,0);lutro.graphics.rectangle('fill',i,223,1,1) end
end
'''
def fixture(folder,initial):
 p=Path(folder);(p/'assets').symlink_to(HERE/'src/assets',target_is_directory=True)
 for name in ('conf.lua','art.lua','techniques.lua','cpu.lua'):(p/name).write_bytes((HERE/'src'/name).read_bytes())
 (p/'main.lua').write_text((HERE/'src/main.lua').read_text()+TELEMETRY+'\nlocal originalLoad=lutro.load\nfunction lutro.load() originalLoad();'+initial+' end\n')
 return p/'main.lua'
def state(core):return dict(zip(FIELDS,[r+g*256 for r,g,b in [core.frame.getpixel((i,223)) for i in range(1,len(FIELDS)+1)]]))
cases=[]
for level in ('easy','medium','hard'):
 for cadence in (2,4,6,10):
  for corner in (False,True):
   mirrored=[]
   for reverse in (False,True):
    x1,x2=(232,320) if corner else (140,228)
    if reverse:x1,x2=384-x1,384-x2
    initial=f'Scene.configure("cpu","{level}");Scene.players[1].x={x1};Scene.players[2].x={x2};Scene.left={2 if reverse else 1};'
    received=blocked=maxcombo=0;previous={};rounds=[]
    with tempfile.TemporaryDirectory() as d:
     with Native(fixture(d,initial)) as core:
      for n in range(3000):
       # A held button never repeats. Alternate real press/release edges only.
       core.step(1,[(0,0)] if n%cadence<cadence//2 else []);s=state(core)
       maxcombo=max(maxcombo,s['combo1'])
       received+=max(0,s['points2']-previous.get('points2',0))
       blocked+=max(0,s['blocks2']-previous.get('blocks2',0))
       if s['result'] and not previous.get('result',0):rounds.append({'winner':s['result']-1,'energy1':s['energy1'],'energy2':s['energy2']})
       previous=s
       if s['winner']:break
      else:raise AssertionError(('Match never ended',level,cadence,corner,reverse,s))
    assert maxcombo<=3,(level,cadence,corner,reverse,maxcombo)
    if level!='easy':assert received>0,(level,cadence,corner,reverse,s)
    if level=='hard' and cadence<=6:assert s['winner']==2,(cadence,corner,reverse,s)
    result={'level':level,'cadence_ticks':cadence,'corner':corner,'reversed':reverse,'cpu_hits':received,'cpu_blocks':blocked,'max_human_combo':maxcombo,'winner':s['winner'],'ticks':s['tick'],'rounds':rounds}
    cases.append(result);mirrored.append({k:v for k,v in result.items() if k not in ('reversed','ticks')})
   assert mirrored[0]==mirrored[1],('Facing changes results',mirrored)
result={'passed':len(cases),'cases':cases,'artifact_sha256':hashlib.sha256((HERE/'dist/deshi-dojo-visual.lutro').read_bytes()).hexdigest(),
 'scope':'Actual historical Lua5.1/x86 core, first P1 sequence given initiative by starting at distance88; ordinary punch input only, same round seed1080. Both facings, open stage/corner, 2/4/6/10tick tap cycles. No injected hits, health changes or CPU input changes. These are reproducible exploit tests, not human win-rate ratings.'}
(HERE/'docs/pressure-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':len(cases),'by_level':{level:{'cpu_match_wins':sum(c['winner']==2 for c in cases if c['level']==level),'cases':16,'cpu_hits':sum(c['cpu_hits'] for c in cases if c['level']==level),'cpu_blocks':sum(c['cpu_blocks'] for c in cases if c['level']==level)} for level in ('easy','medium','hard')}},indent=2))
