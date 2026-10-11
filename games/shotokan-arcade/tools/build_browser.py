"""Offline HTML: same Lua, same palette, tiles, bitmap background and pixel font."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parents[1]
vm=ROOT/'.cache/fengari-web/fengari-web.js'
assert vm.exists(),'Prepare the verified Fengari runtime first.'
lock=json.loads((HERE/'browser/runtime-provenance.json').read_text())
assert hashlib.sha256(vm.read_bytes()).hexdigest()==lock['runtime_sha256'],'Run prepare_browser.py: runtime hash mismatch.'
bridge='''local js=require "js"
local h=js.global.dojoHost
function btn(id) return h:button(id) end
function cls(c) h:clear(c) end
function rect(x,y,w,height,c) h:rect(x,y,w,height,c) end
function rectb(x,y,w,height,c) h:rectb(x,y,w,height,c) end
function line(x1,y1,x2,y2,c) h:line(x1,y1,x2,y2,c) end
function print(text,x,y,c,fixed,scale) h:text(tostring(text),x or 0,y or 0,c or 8,scale or 1) end
function spr(id,x,y,color,scale,flip,rotation,w,height) h:sprite(id,x,y,flip or 0) end
function memcpy(dest,source,size)
 if dest==0 and source==0x8000 and size==16320 then h:background()
 else
  assert(dest==0x7c00 and source>=0xbfc0 and size==32 and (source-0xbfc0)%32==0)
  h:cache(480+(source-0xbfc0)/32)
 end
end
function sfx(id,note,duration,channel,volume,speed) h:sound(id,note,duration,channel,volume) end
'''
code=(HERE/'dist/game.lua').read_text()
bridge+='\n'+code+'''
h.update=function() TIC() end
h.snapshot=function()
 return G.mode.."|"..G.p[1].x.."|"..G.p[2].x.."|"..G.p[1].score.."|"..G.p[2].score.."|"..G.clock.."|"..G.intro.."|"..G.p[1].pose.."|"..G.p[2].pose.."|"..G.frame
end
'''
assets={n:(HERE/'assets'/filename).read_bytes().hex() for n,filename in [('background','dojo.bin'),('tiles','tiles.bin'),('font','font.bin')]}
assets['audio']=json.loads((HERE/'assets/audio.json').read_text())
assets['palette']=json.loads((HERE/'assets/atlas.json').read_text())['palette']
page=(HERE/'browser/template.html').read_text().replace('__VM__',vm.read_text().replace('</script','<\\/script')).replace('__LUA__',json.dumps(bridge).replace('<','\\u003c')).replace('__ASSETS__',json.dumps(assets))
output=HERE/'dist/deshi-dojo-arcade.html'
output.write_text(page)
with zipfile.ZipFile(HERE/'dist/deshi-dojo-arcade.zip','w',zipfile.ZIP_DEFLATED) as z:
 for path in [output,HERE/'dist/shotokan-arcade.tic',HERE/'dist/game.lua',HERE/'dist/SHA256SUMS.txt',HERE/'LICENSE',HERE/'browser/FENGARI-WEB-LICENSE.txt',HERE/'docs/TIC80-LICENSE.txt']:
  z.write(path,path.name)
 if (HERE/'README.md').exists():z.write(HERE/'README.md','LEIA-ME.md')
 for path in sorted((HERE/'docs').iterdir()):
  if path.suffix in ('.png','.gif','.md','.json','.wav'):
   z.write(path,'docs/'+path.name)
 # Include authoring and test source; build commands require the full repository layout.
 for directory in ('src','tools','tests','browser','assets'):
  for path in sorted((HERE/directory).rglob('*')):
   if path.is_file() and '__pycache__' not in path.parts:
    z.write(path,'source/'+str(path.relative_to(HERE)))
 investigation=ROOT/'research/lutro/README.md'
 if investigation.exists():z.write(investigation,'docs/INVESTIGACAO-LUTRO.md')
print('Offline HTML:',len(page.encode()),'bytes; browser and cartridge share the same Lua/art')
