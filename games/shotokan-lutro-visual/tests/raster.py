"""Compare actual historical rendering to Canvas, including cross-cell foot regression."""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image,ImageChops,ImageOps
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'tools'))
from native_host import Native
cases=[{'name':'initial','code':''}]
for level in ('easy','medium','hard'):
 cases.append({'name':'cpu-'+level,'code':f'Scene.configure("cpu","{level}");'})
for choice in range(1,9):
 cases.append({'name':f'arcade-menu-{choice}','code':f'Scene.menu=true;Scene.menuChoice={choice};'})
for body in ('adult','teen','child'):
 for pose in range(1,93):
  for face in (1,-1):
   cases.append({'name':f'{body}-pose-{pose}-face-{face}',
    'code':f'Scene.character(1,{{body="{body}"}});Scene.players[1].pose={pose};Scene.players[1].face={face};'})
 for belt in ('branca','amarela','vermelha','laranja','verde','roxa','marrom','preta'):
  cases.append({'name':f'{body}-belt-{belt}',
   'code':f'Scene.character(1,{{body="{body}",belt="{belt}"}});Scene.character(2,{{body="child"}});'})
for side in (1,2):
 for defense,direction in (('kamae',None),('age',5),('gedan',6),('soto',8 if side==1 else 7),('uchi',7 if side==1 else 8)):
  condition=f'(key==2'+(f' or key=={direction}' if direction else '')+')'
  cases.append({'name':f'guard-{defense}-p{side}','code':f'local down=lutro.joystick.isDown;lutro.joystick.isDown=function(port,key) return port=={side} and {condition} end;for n=1,8 do Scene.advance() end;lutro.joystick.isDown=down;'})
for pose in (35,36,42,47,67,71,75,85,86,89,90,91,92):
 for face in (1,-1):
  for x in (64,320):
   cases.append({'name':f'pose{pose}-face{face}-x{x}',
    'code':f'Scene.players[1].x={x};Scene.players[2].x={280 if x==64 else 104};Scene.players[1].face={face};Scene.players[1].pose={pose};'})
for pose in range(61,77):
 for face,x in ((1,320),(-1,64)):
  cases.append({'name':f'air{pose}-face{face}','code':f'Scene.players[1].x={x};Scene.players[2].x={104 if x==320 else 280};Scene.players[1].face={face};Scene.players[1].pose={pose};Scene.players[1].height=44;Scene.players[1].air=true;Scene.players[1].phase="SALTO";'})
# The extended foot must stay on its own pose; the next pose has no orphan foot.
a=Image.open(HERE/'src/assets/pose-35.png').convert('RGBA')
b=Image.open(HERE/'src/assets/pose-36.png').convert('RGBA')
assert a.getchannel('A').crop((208,0,224,144)).getbbox(),'Missing extended mawashi foot'
assert not b.getchannel('A').crop((0,0,60,144)).getbbox(),'Orphan foot imported from previous pose'
left=Image.open(HERE/'src/assets/fighter-left.png').convert('RGBA')
for pose in range(1,json.loads((HERE/'assets/import.json').read_text())['frames']+1):
 q=((pose-1)%4*224,(pose-1)//4*144)
 mirrored=left.crop((q[0],q[1],q[0]+224,q[1]+144))
 assert mirrored.tobytes()==ImageOps.mirror(Image.open(HERE/f'src/assets/pose-{pose:02d}.png').convert('RGBA')).tobytes(),pose
with tempfile.TemporaryDirectory(prefix='dojo-raster-') as tmp:
 folder=Path(tmp);fixture=folder/'fixture';fixture.mkdir();(fixture/'assets').symlink_to(HERE/'src/assets',target_is_directory=True)
 for name in ('conf.lua','art.lua','techniques.lua','cpu.lua','characters.lua','character_data.lua'):(fixture/name).write_bytes((HERE/'src'/name).read_bytes())
 for c in cases:
  (fixture/'main.lua').write_text((HERE/'src/main.lua').read_text()+ '\nfunction lutro.update(dt) end\nlocal originalLoad=lutro.load\nfunction lutro.load() originalLoad();Scene.configure("versus","easy");'+c['code']+' end\n')
  with Native(fixture/'main.lua') as core:
   core.step(1);core.frame.save(folder/(c['name']+'-native.png'))
 (folder/'cases.json').write_text(json.dumps(cases))
 subprocess.run(['node',str(HERE/'tests/raster.cjs'),str(folder)],check=True,timeout=120)
 for c in cases:
  native=Image.open(folder/(c['name']+'-native.png')).convert('RGB')
  browser=Image.open(folder/(c['name']+'-browser.png')).convert('RGB')
  diff=ImageChops.difference(native,browser)
  assert not diff.getbbox(),(c['name'],diff.getbbox())
result={'initial_scene_equal':True,'frames_equal':len(cases),'all_92_poses_mirrored':True,
 'cross_cell_mawashi_foot_recovered':True,'orphan_foot_absent':True,'resolution':[384,224],
 'cart_sha256':hashlib.sha256((HERE/'dist/deshi-dojo-visual.lutro').read_bytes()).hexdigest(),
 'scope':'Actual historical x86-64 software draw vs offline Chromium pixels: initial scene, wall/facing strike poses, all airborne poses at height44, reactions and low planted stance, three CPU HUD ranks and four menu choices. Hardware Pi pending.'}
(HERE/'docs/raster-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
