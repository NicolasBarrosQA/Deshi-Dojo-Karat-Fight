"""Pack the visual proof as a historical .lutro ZIP and standalone offline HTML."""
from pathlib import Path
import unicodedata
import argparse,base64,hashlib,json,zipfile,os,time
parser=argparse.ArgumentParser(description='Build offline Shotokan browser/cart packages')
parser.add_argument('--web-only',action='store_true',help='Generate only the HTML for local development')
parser.add_argument('--archives',action='store_true',help='Also generate legacy optional delivery ZIPs')
args=parser.parse_args()
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
dist=HERE/'dist';dist.mkdir(exist_ok=True)
def publish(source,target):
 # Windows cloud sync can briefly open a package without delete-sharing.
 for attempt in range(25):
  try:source.replace(target);return
  except OSError as error:
   if attempt==24 or getattr(error,'winerror',None) not in (5,32) and error.errno!=22:raise
   time.sleep(.2)
html_tmp=dist/('html-build-'+str(os.getpid())+'.tmp')
cart_tmp=dist/('cart-build-'+str(os.getpid())+'.tmp')
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
techniques.update(json.loads((HERE/'assets/specials.json').read_text(encoding='utf-8')))
(HERE/'src/techniques.lua').write_text('return '+lua(techniques)+'\n',encoding='utf-8')
characters=json.loads((HERE/'assets/characters.json').read_text(encoding='utf-8'))
characters['bodies']=json.loads((HERE/'assets/character-assets.json').read_text(encoding='utf-8'))
from character_registry import validate,visual_key
characters['visual_profiles']=json.loads((HERE/'assets/character-visuals.json').read_text(encoding='utf-8')) if (HERE/'assets/character-visuals.json').exists() else {}
characters['student_order']=list(characters['students'])
characters['specials']=json.loads((HERE/'assets/special-assets.json').read_text(encoding='utf-8')) if (HERE/'assets/special-assets.json').exists() else {}
if characters['specials']:
 import subprocess,sys
 compiler=sys.executable
 try:import PIL,numpy
 except ImportError:
  bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
  if bundled.is_file():compiler=str(bundled)
 for id,old in characters['students'].items():
  if old.get('visual'):assert old['visual']==visual_key(validate({'id':id,**old},characters,characters['bodies'])),'Aparencia alterada sem exportar no editor: '+id
 subprocess.run([compiler,str(HERE/'tools/refresh_registered_profiles.py')],check=True)
 characters['visual_profiles']=json.loads((HERE/'assets/character-visuals.json').read_text(encoding='utf8'))
 subprocess.run([compiler,str(HERE/'tools/compile_special_profiles.py')],check=True)
 characters['special_profiles']={k:v['groups'] for k,v in json.loads((HERE/'assets/special-profiles.json').read_text(encoding='utf-8')).items()}
else:characters['special_profiles']={}
for id,student in list(characters['students'].items()):
 assert student.get('id',id)==id,'ID do cadastro nao corresponde a chave: '+id
 student=validate({'id':id,**student},characters,characters['bodies'])
 old=characters['students'][id]
 if old.get('visual'):
  assert old['visual']==visual_key(student),'Aparencia alterada sem exportar no editor: '+id
  assert old['visual'] in characters['visual_profiles'],'Perfil visual inexistente: '+id
  student['visual']=old['visual'];student['portrait']=old.get('portrait','')
 characters['students'][id]=student
 student['display_name']=unicodedata.normalize('NFKD',student['name']).encode('ascii','ignore').decode().upper()[:20]
 student['display_nickname']=unicodedata.normalize('NFKD',student.get('nickname','')).encode('ascii','ignore').decode().upper()[:16]
active_visuals={s['visual'] for s in characters['students'].values() if s.get('visual')}
characters['visual_profiles']={k:v for k,v in characters['visual_profiles'].items() if k in active_visuals}
characters['special_profiles']={k:v for k,v in characters['special_profiles'].items() if k in active_visuals}
(HERE/'src/character_data.lua').write_text('return '+lua(characters)+'\n',encoding='utf-8')
modules=''
for name in ('art','techniques','motion','specials','cpu','character_data','characters'):
 modules+="package.preload['"+name+"']=function()\n"+(HERE/'src'/f'{name}.lua').read_text(encoding='utf-8')+'\nend\n'
active_visuals={s['visual'] for s in characters['students'].values() if s.get('visual')}
characters['visual_profiles']={k:v for k,v in characters['visual_profiles'].items() if k in active_visuals}
visual_names=set()
special_names=set()
character_names=set()
for body in characters['bodies'].values():
 for variants in body['parts'].values():
  for part in variants.values():character_names.update(part[side] for side in ('right','left'))
for groups in [*characters['specials'].values(),*characters['special_profiles'].values()]:
 for animation in groups.values():
  for part in [animation['body'],*animation['belts'].values()]:special_names.update(part[side] for side in ('right','left'))
for profile in characters['visual_profiles'].values():
 visual_names.add(profile['portrait'])
 for part in [profile['parts']['body'],*profile['parts']['belt'].values()]:
  visual_names.update(part[side] for side in ('right','left'))
def runtime_asset(p):
 if p.stem.startswith('identity-thumbnail-'):return False
 if p.stem.startswith('special-'):return p.stem in special_names
 if p.stem.startswith(('char-visual-','char-geometry-','portrait-')):return p.stem in visual_names
 if p.stem.startswith('char-'):return p.stem in character_names
 return not p.stem.startswith('pose-') and p.stem not in ('fighter-right','fighter-left')
payload={p.stem:'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode() for p in sorted((HERE/'src/assets').glob('*.png')) if runtime_asset(p)}
page=(HERE/'browser/template.html').read_text(encoding='utf-8')
page=page.replace('__VM__',runtime_bytes.decode('utf-8').replace('</script','<\\/script'))
page=page.replace('__ASSETS__',json.dumps(payload)).replace('__LUA__',json.dumps(modules+(HERE/'src/main.lua').read_text(encoding='utf-8')).replace('<','\\u003c'))
sounds={p.stem:'data:audio/wav;base64,'+base64.b64encode(p.read_bytes()).decode() for p in sorted((HERE/'src/assets').glob('special-*.wav'))}
page=page.replace('__SOUNDS__',json.dumps(sounds))
page=page.replace('__TECHNIQUES__',json.dumps(techniques,ensure_ascii=False)).replace('__ATLAS_HEIGHT__',str(json.loads((HERE/'assets/import.json').read_text(encoding='utf-8'))['atlas_size'][1]))
page=page.replace('__CHARACTER_OPTIONS__',json.dumps(json.loads((HERE/'assets/characters.json').read_text(encoding='utf-8')),ensure_ascii=False))
html_tmp.write_text(page,encoding='utf-8');publish(html_tmp,dist/'deshi-dojo-visual.html')
if args.web_only:
 print('HTML atualizado: deshi-dojo-visual.html')
 raise SystemExit(0)
with zipfile.ZipFile(cart_tmp,'w',zipfile.ZIP_DEFLATED) as z:
 def entry(name,data):
  # Stable metadata makes the cart byte-identical across rebuilds.
  info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(info,data)
 # The 2019 extractor requires directory entries before their files.
 entry('assets/',b'')
 for p in sorted((HERE/'src').rglob('*')):
  if p.is_file() and p.suffix!='.json' and (p.suffix!='.png' or runtime_asset(p)):entry(p.relative_to(HERE/'src').as_posix(),p.read_bytes())
publish(cart_tmp,dist/'deshi-dojo-visual.lutro')
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dist.iterdir() if p.suffix in ('.html','.lutro')}
(dist/'SHA256SUMS.txt').write_text(''.join(f'{h}  {n}\n' for n,h in sorted(hashes.items())))
if not args.archives:
 print('Built offline HTML and historical .lutro:',hashes)
 raise SystemExit(0)
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
 for name in ('FUNDAMENTOS.md','COMPATIBILIDADE.md','CPU.md','cpu-native-results.json','cpu-browser-results.json','research-sources.json','native-results.json','browser-results.json','capture-results.json','raster-results.json','preservation-results.json','TIC80-LICENSE.txt'):
  p=HERE/'docs'/name
  if p.exists():z.write(p,'docs/'+name)
 z.write(HERE/'browser/FENGARI-WEB-LICENSE.txt','licenses/FENGARI-WEB-LICENSE.txt')
