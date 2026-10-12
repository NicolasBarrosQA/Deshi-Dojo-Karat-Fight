"""Reconstruct proposed identity frames for individual visual inspection."""
import json
from PIL import Image,ImageDraw
from pathlib import Path
from compile_character import layer_frames
from character_registry import read,DEFAULT
from identity_art import catalog,attachments,replace,head
from prepare_identity_pilots import unpack
HERE=Path(__file__).resolve().parents[1]

def run():
    out=HERE/'docs/identity-pilots';out.mkdir(exist_ok=True)
    manifest=read(HERE/'assets/character-assets.json');specials=read(HERE/'assets/special-assets.json')['adult']
    base=[Image.new('RGBA',(224,144)) for _ in range(92)]
    for layer in ('body','face','hair','foreground'):
        for i,f in enumerate(layer_frames('adult',layer,'default',manifest)):base[i].alpha_composite(f)
    foreground=layer_frames('adult','foreground','default',manifest)
    belts=layer_frames('adult','belt','preta',manifest)
    selected=[('base',1),('base',15),('base',39),('base',55),('base',75),('base',85),('ashi_finish',6),('knockdown',5),('knockdown',8)]
    montage=Image.new('RGB',(224*9,170*4),'#243139');draw=ImageDraw.Draw(montage);records=[]
    for row,identity in enumerate(catalog()['bodies']['adult']):
        student={'body':'adult','identity':identity,'appearance':DEFAULT}
        for group,originals in [('base',base),*[(k,unpack(v['body'])) for k,v in specials.items()]]:
            bindings=attachments('adult',group);cloth=belts if group=='base' else unpack(specials[group]['belts']['preta'])
            for i,original in enumerate(originals):
                frame,_=replace(original,student,bindings[i],foreground[i] if group=='base' else None);frame.alpha_composite(cloth[i])
                name=f'{identity}-{group}-{i+1:02}.png';frame.save(out/name)
                records.append({'identity':identity,'group':group,'pose':i+1,'file':name,'attachment':bindings[i]})
                if (group,i+1) in selected:
                    col=selected.index((group,i+1));montage.paste(frame,(col*224,row*170+23),frame);draw.text((col*224+4,row*170+5),f'{identity} / {group} {i+1}',fill='white')
    montage.save(out/'pilot-poses.png')
    (out/'audit.json').write_text(json.dumps(records,indent=2)+'\n')
    page='''<!doctype html><meta charset="utf-8"><title>Identidades · revisão de poses</title><style>body{background:#243139;color:white;font:16px system-ui;margin:24px}img{image-rendering:pixelated;background:#243139}select{font:inherit;padding:8px;margin:8px}#grid{display:grid;grid-template-columns:repeat(4,1fr)}#grid img{width:100%;max-width:448px}</style><h1>Identidades · poses reais recompostas</h1><p>Use a mesma pose para comparar os quatro personagens. Revisão visual, sem alegação automática de anatomia correta.</p><select id="group"></select><select id="pose"></select><div id="grid"></div><script>const rows=__DATA__,g=document.querySelector('#group'),p=document.querySelector('#pose'),grid=document.querySelector('#grid');for(const k of [...new Set(rows.map(x=>x.group))])g.add(new Option(k,k));function draw(){grid.replaceChildren();for(const r of rows.filter(x=>x.group===g.value&&x.pose===+p.value)){const d=document.createElement('div');d.textContent=r.identity;const im=new Image();im.src=r.file;im.width=448;d.append(im);grid.append(d)}}function groups(){p.replaceChildren();for(const k of [...new Set(rows.filter(x=>x.group===g.value).map(x=>x.pose))])p.add(new Option(k,k));draw()}g.onchange=groups;p.onchange=draw;groups();</script>'''.replace('__DATA__',json.dumps(records))
    (out/'index.html').write_text(page,encoding='utf8')
    # Head/neck contact pages retain crossing arms and the actual surrounding gi.
    logical=[(g,p) for g,p in [(r['group'],r['pose']) for r in records if r['identity']=='cacheada']]
    identities=list(catalog()['bodies']['adult'])
    for start in range(0,len(logical),8):
        contact=Image.new('RGB',(1280,900),'#243139');d=ImageDraw.Draw(contact)
        for col,(group,pose) in enumerate(logical[start:start+8]):
            binding=attachments('adult',group)[pose-1]
            boxes=[head({'body':'adult','identity':key},binding).getbbox() for key in identities]
            cx=(min(b[0] for b in boxes)+max(b[2] for b in boxes))//2;cy=(min(b[1] for b in boxes)+max(b[3] for b in boxes))//2
            for row,key in enumerate(['original',*identities]):
                im=base[pose-1] if key=='original' and group=='base' else unpack(specials[group]['body'])[pose-1] if key=='original' else Image.open(out/f'{key}-{group}-{pose:02}.png')
                crop=im.crop((cx-32,cy-32,cx+32,cy+32)).resize((160,160),Image.Resampling.NEAREST)
                contact.paste(crop,(col*160,row*180+20),crop)
                d.text((col*160+3,row*180+4),f'{key} {group} {pose}',fill='white')
        contact.save(out/f'head-review-{start//8+1:02}.png')
    print('Reconstructed',len(records),'individual identity frames for visual review')

if __name__=='__main__':run()
