"""Bundle the unchanged prototype Lua and an integrity-verified Lua 5.3 VM."""
from pathlib import Path
import json
import hashlib
import zipfile
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
vm=ROOT/'.cache/fengari-web/fengari-web.js'
if not vm.exists():raise SystemExit('Prepare o runtime fengari-web verificado no cache.')
bridge='''local js=require "js"
local h=js.global.dojoHost
function btn(id) return h:button(id) end
function cls(c) h:clear(c) end
function rect(x,y,w,height,c) h:rect(x,y,w,height,c) end
function rectb(x,y,w,height,c) h:rectb(x,y,w,height,c) end
function line(x1,y1,x2,y2,c) h:line(x1,y1,x2,y2,c) end
function print(text,x,y,c) h:text(tostring(text),x or 0,y or 0,c or 12) end
'''
source=(HERE.parent/'src/dojo.lua').read_text()
bridge+='\n'+source+'''
h.update=function() TIC() end
h.snapshot=function()
 return DD.mode.."|"..DD.p[1].x.."|"..DD.p[2].x.."|"..DD.p[1].points.."|"..DD.p[2].points.."|"..DD.frame
end
'''
page=(HERE/'template.html').read_text().replace('__VM__',vm.read_text().replace('</script','<\\/script')).replace('__LUA__',json.dumps(bridge,ensure_ascii=True).replace('<','\\u003c'))
output=HERE/'deshi-dojo-jogar.html'
output.write_text(page)
with zipfile.ZipFile(HERE/'deshi-dojo-jogar.zip','w',zipfile.ZIP_DEFLATED) as z:
 for path in [output,HERE/'FENGARI-WEB-LICENSE.txt',HERE/'runtime-provenance.json',HERE.parent/'LICENSE']:
  z.write(path,path.name)
 if (HERE/'README.md').exists():
  z.write(HERE/'README.md','LEIA-ME.md')
print(output,'bytes',output.stat().st_size,'sha256',hashlib.sha256(output.read_bytes()).hexdigest())
