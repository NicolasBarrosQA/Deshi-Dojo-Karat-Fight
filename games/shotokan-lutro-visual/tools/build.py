"""Pack the visual proof as a historical .lutro ZIP and standalone offline HTML."""
from pathlib import Path
import argparse,base64,hashlib,json,zipfile
parser=argparse.ArgumentParser(description='Build offline Shotokan browser/cart packages')
parser.add_argument('--web-only',action='store_true',help='Generate only the HTML for local development')
args=parser.parse_args()
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
dist=HERE/'dist';dist.mkdir(exist_ok=True)
runtime=HERE/'browser/fengari-web.js'
lock=json.loads((HERE/'browser/runtime-provenance.json').read_text(encoding='utf-8'))
runtime_original=runtime.read_bytes()
# Older Windows clones may already contain Git's automatic LF -> CRLF conversion.
# Only accept that conversion when the restored bytes match the original pin.
runtime_bytes=runtime_original.replace(b'\r\n',b'\n')
if hashlib.sha256(runtime_bytes).hexdigest()!=lock['runtime_sha256']:
 raise SystemExit('Falha de integridade no Fengari: o conteúdo difere da versão verificada. O interpretador não será usado.')
if runtime_bytes!=runtime_original:
 runtime.write_bytes(runtime_bytes)
 print('Quebras de linha do Fengari restauradas; SHA-256 original confirmado.')
def lua(value):
 if isinstance(value,str):return json.dumps(value,ensure_ascii=False)
 if isinstance(value,bool):return 'true' if value else 'false'
 if isinstance(value,(int,float)):return str(value)
 if isinstance(value,list):return '{'+','.join(lua(v) for v in value)+'}'
 if isinstance(value,dict):return '{'+','.join('['+lua(k)+']='+lua(v) for k,v in value.items())+'}'
 raise TypeError(value)
techniques=json.loads((HERE/'assets/techniques.json').read_text(encoding='utf-8'))
(HERE/'src/techniques.lua').write_text('return '+lua(techniques)+'\n',encoding='utf-8')
modules=''
for name in ('art','techniques'):
 modules+="package.preload['"+name+"']=function()\n"+(HERE/'src'/f'{name}.lua').read_text(encoding='utf-8')+'\nend\n'
payload={p.stem:'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode() for p in sorted((HERE/'src/assets').glob('*.png')) if not p.stem.startswith('pose-')}
page=(HERE/'browser/template.html').read_text(encoding='utf-8')
page=page.replace('__VM__',runtime_bytes.decode('utf-8').replace('</script','<\\/script'))
page=page.replace('__ASSETS__',json.dumps(payload)).replace('__LUA__',json.dumps(modules+(HERE/'src/main.lua').read_text(encoding='utf-8')).replace('<','\\u003c'))
page=page.replace('__TECHNIQUES__',json.dumps(techniques,ensure_ascii=False)).replace('__ATLAS_HEIGHT__',str(json.loads((HERE/'assets/import.json').read_text(encoding='utf-8'))['atlas_size'][1]))
(dist/'deshi-dojo-visual.html').write_text(page,encoding='utf-8')
if args.web_only:
 print('HTML atualizado: deshi-dojo-visual.html')
 raise SystemExit(0)
with zipfile.ZipFile(dist/'deshi-dojo-visual.lutro','w',zipfile.ZIP_DEFLATED) as z:
 def entry(name,data):
  # Stable metadata makes the cart byte-identical across rebuilds.
  info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(info,data)
 # The 2019 extractor requires directory entries before their files.
 entry('assets/',b'')
 for p in sorted((HERE/'src').rglob('*')):
  if p.is_file() and not p.name.startswith('pose-'):entry(str(p.relative_to(HERE/'src')),p.read_bytes())
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dist.iterdir() if p.suffix in ('.html','.lutro')}
(dist/'SHA256SUMS.txt').write_text(''.join(f'{h}  {n}\n' for n,h in sorted(hashes.items())))
with zipfile.ZipFile(dist/'deshi-dojo-visual.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(HERE.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or p.parent==dist and p.suffix=='.zip':continue
  if dist in p.parents and p.parent!=dist:continue
  name=str(p.relative_to(HERE))
  z.write(p,name.removeprefix('dist/') if p.parent==dist else name)
print('Built standalone offline HTML, historical .lutro and source ZIP:',hashes)

# Smaller ready-to-play delivery; the other ZIP retains source and art.
with zipfile.ZipFile(dist/'deshi-dojo-fundamentos.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ('deshi-dojo-visual.html','deshi-dojo-visual.lutro','SHA256SUMS.txt'):
  z.write(dist/name,name)
 z.write(HERE/'README.md','LEIA-ME.md')
 z.write(HERE/'LICENSE','LICENSE')
 for name in ('FUNDAMENTOS.md','COMPATIBILIDADE.md','research-sources.json','native-results.json','browser-results.json','capture-results.json','raster-results.json','preservation-results.json','TIC80-LICENSE.txt'):
  p=HERE/'docs'/name
  if p.exists():z.write(p,'docs/'+name)
 z.write(HERE/'browser/FENGARI-WEB-LICENSE.txt','licenses/FENGARI-WEB-LICENSE.txt')
