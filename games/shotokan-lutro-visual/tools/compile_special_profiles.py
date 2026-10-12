"""Bake creator appearance into authored special frames; never modifies the roster."""
import json,sys,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
def compile_all():
 source=HERE/'assets/special-assets.json';target=HERE/'assets/special-profiles.json'
 if not source.exists():return
 bases=json.loads(source.read_text());roster=json.loads((HERE/'assets/characters.json').read_text())
 ceremony=HERE/'assets/ceremony-assets.json'
 if ceremony.exists():
  for body,animation in json.loads(ceremony.read_text()).items():bases[body]['ceremony']=animation
 touch=HERE/'assets/hand-touch-assets.json'
 if touch.exists():
  for body,animation in json.loads(touch.read_text()).items():bases[body]['hand_touch']=animation
 result=json.loads(target.read_text()) if target.exists() else {}
 from identity_art import sources as identity_sources,attachments,replace,paint,head
 from hair_art import sources as hair_sources,styles as hair_styles,apply as apply_hair,logical_bounds
 signatures={}
 body_signatures={}
 for body,groups in bases.items():
  digest=hashlib.sha256(source.read_bytes()+Path(__file__).read_bytes()+(HERE/'tools/compile_character.py').read_bytes()+(HERE/'tools/character_registry.py').read_bytes()+(HERE/'tools/skin_palette.py').read_bytes())
  if ceremony.exists():digest.update(ceremony.read_bytes())
  if touch.exists():digest.update(touch.read_bytes())
  for group in groups.values():
   for part in [group['body'],*group['belts'].values()]:digest.update((HERE/'src/assets'/(part['right']+'.png')).read_bytes())
  body_signatures[body]=digest.digest()
 for s in roster['students'].values():
  if not s.get('visual'):continue
  digest=hashlib.sha256(body_signatures[s['body']])
  for p in identity_sources(s):digest.update(p.read_bytes())
  for p in hair_sources(s):digest.update(p.read_bytes())
  signatures[s['visual']]=digest.hexdigest()
 needed=list({s['visual']:s for s in roster['students'].values() if s.get('visual') and result.get(s['visual'],{}).get('signature')!=signatures[s['visual']]}.values())
 if not needed:return
 from PIL import Image,ImageFilter
 from compile_character import pack,skin,shade,transform
 from skin_palette import apply_skin_palette
 from character_registry import SKINS,HAIR_COLORS,visual_key
 from character_masks import components
 neutral_bodies=json.loads((HERE/'assets/character-assets.json').read_text())
 def unpack(part):
  atlas=Image.open(HERE/'src/assets'/(part['right']+'.png')).convert('RGBA');frames=[]
  for f in part['frames']:
   im=Image.new('RGBA',(224,144));im.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']));frames.append(im)
  return frames
 for s in needed:
  key=s['visual'];ap=s['appearance'];groups={}
  gkey=visual_key({**s,'face':'default','hair':'default','beard':'default','identity':'default','appearance':{'height':ap['height'],'build':ap['build']}})
  for group,a in bases[s['body']].items():
   originals=unpack(a['body']);frames=[]
   for index,im in enumerate(originals):
    if s.get('hair') in hair_styles():
     frames.append(transform(apply_hair(apply_skin_palette(im,ap['skin']),s,group,index),ap,a['bounds'][index]));continue
    if s.get('identity','default')!='default':
     binding=attachments(s['body'],group)[index]
     im=paint(replace(im,s,binding)[0],s,head(s,binding))
     frames.append(transform(im,ap,a['bounds'][index]));continue
    if HAIR_COLORS.get(ap['hair_color']) is None or neutral_bodies[s['body']].get('revision')=='neutral-2d-v3':
     frames.append(transform(apply_skin_palette(im,ap['skin']),ap,a['bounds'][index]));continue
    hair=Image.new('L',im.size)
    im=apply_skin_palette(im,ap['skin'])
    for y in range(144):
     for x in range(224):
      r,g,b,alpha=im.getpixel((x,y))
      if alpha and max(r,g,b)<105:hair.putpixel((x,y),255)
    core=hair.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3));parts=components(core);mask=Image.new('L',im.size)
    if parts:
     for i in parts[0]:mask.putpixel((i%224,i//224),255)
     mask=mask.filter(ImageFilter.MaxFilter(3))
    for y in range(144):
     for x in range(224):
      r,g,b,alpha=im.getpixel((x,y))
      if not alpha:continue
      if HAIR_COLORS[ap['hair_color']] and mask.getpixel((x,y)) and 23<max(r,g,b)<105 and not skin((r,g,b)):
       light=.35+.65*min(1,max(r,g,b)/110);im.putpixel((x,y),(*(min(255,round(c*light)) for c in HAIR_COLORS[ap['hair_color']]),alpha))
    frames.append(transform(im,ap,a['bounds'][index]))
   rec={'body':pack(frames,f'special-profile-{key}-{group}',HERE/'src/assets'),'belts':{},'bounds':[]}
   if a.get('touch'):
    from PIL import ImageDraw
    rec['touch']=[]
    for point in a['touch']:
     marker=Image.new('RGBA',(224,144));ImageDraw.Draw(marker).rectangle((point['x']-2,point['top'],point['x'],point['bottom']-1),fill='white')
     bounds=transform(marker,ap,a['bounds'][point['frame']-1]).getbbox()
     rec['touch'].append({'frame':point['frame'],'x':bounds[2]-1,'top':bounds[1],'bottom':bounds[3]})
   for belt,part in a['belts'].items():
    belts=[transform(im,ap,a['bounds'][i]) for i,im in enumerate(unpack(part))]
    rec['belts'][belt]=pack(belts,f'special-geometry-{gkey}-{group}-belt-{belt}',HERE/'src/assets')
    if belt=='preta':
     for im,b in zip(frames,belts):
      one=logical_bounds(im);two=logical_bounds(b) if b.getbbox() else one
      rec['bounds'].append([min(one[0],two[0]),min(one[1],two[1]),max(one[2],two[2]),max(one[3],two[3])])
   groups[group]=rec
  result[key]={'signature':signatures[key],'identity':s.get('identity','default'),'groups':groups}
 target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':compile_all()
