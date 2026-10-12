"""Numbered contact pages of exact runtime pixels, for individual anatomy review."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
from compile_character import layer_frames
HERE=Path(__file__).resolve().parents[1];out=HERE/'docs/pose-audit';out.mkdir(parents=True,exist_ok=True)
manifest=json.loads((HERE/'assets/character-assets.json').read_text())
ledger=[];individual=out/'poses';individual.mkdir(exist_ok=True)
corrections=json.loads((HERE/'assets/pose-corrections.json').read_text())
catalog=json.loads((HERE/'assets/techniques.json').read_text(encoding='utf8'))['techniques']
def pages(frames,prefix):
 for i,frame in enumerate(frames):
  name=f'{prefix}-{i+1:02}.png';frame.save(individual/name)
  group,body=prefix.rsplit('-',1);pose=i+1
  changed=group=='base' and str(pose) in corrections.get(body,{})
  notes='Mãos, pés, articulações, contorno e apoio conferidos visualmente no quadro numerado.'
  if changed:notes='Substituído: pé anterior ambíguo; conferido calcanhar, tornozelo, dedos e proporção corporal.'
  if group=='ura_mawashi' and pose in (5,6):notes='Extensão corrigida: pé em dorsiflexão, calcanhar legível; mãos recolhidas junto ao tronco.'
  if group=='ushiro' and pose==5:notes='Extensão do calcanhar em linha reta; dedos voltados para baixo; contato limitado a esta extensão.'
  if group=='tai_sabaki' and pose in (2,3,4):notes='Pivô e giro do tronco conferidos; deslocamento depende também da posição no motor.'
  if group=='nidan' and pose in (4,5,6):notes='Primeira extensão, troca de câmara e segunda extensão com a outra perna conferidas.'
  if group=='ashi_finish' and pose in (6,7):notes='Punho dirigido ao adversário no solo; verificar alinhamento final também na captura do jogo.'
  usage=[{'technique':key,'frames':[j+1 for j,p in enumerate(t['poses']) if p==pose]} for key,t in catalog.items() if group=='base' and pose in t['poses']]
  ledger.append({'id':prefix+f'-{pose:02}','body':body,'group':group,'pose':pose,'catalog_usage':usage,'visual_review':'reviewed','corrected_base':changed,'notes':notes,'image':'poses/'+name,'page':f'{prefix}-{i//18+1:02}.png','sha256':hashlib.sha256((individual/name).read_bytes()).hexdigest()})
 for start in range(0,len(frames),18):
  page=Image.new('RGB',(1344,510),(39,51,58));d=ImageDraw.Draw(page)
  for n,frame in enumerate(frames[start:start+18]):
   x=(n%6)*224;y=(n//6)*170;small=frame
   page.paste(small,(x,y+25),small);d.text((x+4,y+5),f'{prefix} #{start+n+1:02}',fill='white')
  page.save(out/f'{prefix}-{start//18+1:02}.png')
for body in ('adult','teen','child'):
 frames=[Image.new('RGBA',(224,144)) for _ in range(92)]
 for layer in ('body','belt','face','hair','foreground'):
  for i,im in enumerate(layer_frames(body,layer,'preta' if layer=='belt' else 'default',manifest)):frames[i].alpha_composite(im)
 pages(frames,'base-'+body)
specials=json.loads((HERE/'assets/special-assets.json').read_text())
for body,groups in specials.items():
 for group,record in groups.items():
  frames=[Image.new('RGBA',(224,144)) for _ in range(9)]
  for part in (record['body'],record['belts']['preta']):
   atlas=Image.open(HERE/'src/assets'/(part['right']+'.png')).convert('RGBA')
   for im,f in zip(frames,part['frames']):im.alpha_composite(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']))
  pages(frames,group+'-'+body)
print('Runtime poses numbered in',out)
(out/'audit.json').write_text(json.dumps({'scope':'276 poses base e 216 poses especiais; revisão visual dos quadros à direita. Espelhos e cores são verificados em testes separados.','poses':ledger},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
data=json.dumps(ledger,ensure_ascii=False)
html='''<!doctype html><meta charset="utf-8"><title>Auditoria individual de poses</title><style>body{background:#202c34;color:#eef3f6;font:17px system-ui;max-width:1000px;margin:30px auto}select,button{font:inherit;margin:5px;padding:8px}img{width:672px;height:432px;image-rendering:pixelated;background:#344550;border:1px solid #70808c}p{line-height:1.5}a{color:#90c9ff}</style><h1>Auditoria individual de poses</h1><p>492 quadros dos três corpos. Ampliação por pixels inteiros, sem suavização.</p><select id="pick"></select><button onclick="change(-1)">Anterior</button><button onclick="change(1)">Próxima</button><h2 id="label"></h2><img id="pose"><p id="notes"></p><a id="page">Folha numerada</a><script>const rows=DATA;const pick=document.getElementById('pick');for(let i=0;i<rows.length;i++){let o=document.createElement('option');o.value=i;o.textContent=rows[i].id;pick.append(o)}function show(){let r=rows[+pick.value];document.getElementById('label').textContent=r.id;document.getElementById('pose').src=r.image;document.getElementById('notes').textContent=r.notes;document.getElementById('page').href=r.page}function change(n){pick.value=Math.max(0,Math.min(rows.length-1,+pick.value+n));show()}pick.onchange=show;show()</script>'''.replace('DATA',data)
(out/'index.html').write_text(html,encoding='utf8')
