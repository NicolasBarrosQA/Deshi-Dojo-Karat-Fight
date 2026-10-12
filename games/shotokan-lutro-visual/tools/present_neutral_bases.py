"""Package authored approval images; only layout/resize, no anatomy generation."""
import json,hashlib,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parents[1];SOURCE=HERE/'assets/source/avatar-bases-v2';OUT=HERE/'docs/avatar-bases-v2';OUT.mkdir(parents=True,exist_ok=True)
names=[['crianca-masculina','adolescente-masculino','adulto-masculino'],['crianca-feminina','adolescente-feminina','adulta-feminina']]
labels=[['Criança · masculino','Adolescente · masculino','Adulto · masculino'],['Criança · feminino','Adolescente · feminino','Adulta · feminino']]
heights=[[510,675,780],[510,660,765]]
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',32);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24);title=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',46)
canvas=Image.new('RGB',(2100,1980),'#edf0ef');draw=ImageDraw.Draw(canvas);draw.text((56,28),'DESHI DOJO · SEIS BASES NEUTRAS',font=title,fill='#23333a');draw.text((56,90),'Uma pose frontal · carecas · sem feições · avaliação de traço e proporções',font=small,fill='#52646a')
records=[]
for row,items in enumerate(names):
    floor=1010 if row==0 else 1915
    for col,name in enumerate(items):
        path=SOURCE/(name+'.png');im=Image.open(path).convert('RGBA');alpha=im.getchannel('A');box=alpha.point(lambda v:255 if v>=32 else 0).getbbox();assert box,(name,'empty')
        assert alpha.getextrema()[0]==0,(name,'not transparent')
        crop=im.crop(box);height=heights[row][col];w=round(crop.width*height/crop.height)
        display=crop.resize((w,height),Image.Resampling.LANCZOS);x=col*700+(700-w)//2;y=floor-height
        canvas.paste(display,(x,y),display)
        label=labels[row][col];text_box=draw.textbbox((0,0),label,font=font);tx=col*700+(700-(text_box[2]-text_box[0]))//2
        draw.text((tx,160 if row==0 else 1095),label,font=font,fill='#23333a')
        records.append({'id':name,'label':label,'file':str(path.relative_to(HERE)),'width':im.width,'height':im.height,'alpha_range':alpha.getextrema(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'display_height':height})
draw.line((45,1050,2055,1050),fill='#c6d0cf',width=2)
canvas.save(OUT/'seis-bases-neutras.png')
(OUT/'manifest.json').write_text(json.dumps({'status':'visual concepts for approval; not rigged 3D models or separated production layers','tool':'built-in image_gen','pose':'front neutral A-pose','images':records},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cards=[]
for r in records:
    cards.append('<figure><figcaption>'+r['label']+'</figcaption><a href="../../'+r['file']+'"><img src="../../'+r['file']+'" alt="'+r['label']+'"></a></figure>')
page='<!doctype html><meta charset="utf-8"><title>Deshi Dojo · bases neutras</title><style>body{background:#edf0ef;color:#23333a;font:18px system-ui;margin:32px}main{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}figure{margin:0;background:white;padding:16px;border-radius:8px}img{width:100%;height:600px;object-fit:contain}a{color:inherit}figcaption{font-weight:600}@media(max-width:900px){main{grid-template-columns:repeat(2,1fr)}img{height:420px}}</style><h1>Seis bases neutras</h1><p>Referências visuais em uma pose padrão, antes da modelagem e das animações. Clique em uma imagem para examinar o PNG original.</p><main>'+''.join(cards)+'</main>'
(OUT/'index.html').write_text(page,encoding='utf8')
with zipfile.ZipFile(OUT/'seis-bases-neutras.zip','w',zipfile.ZIP_DEFLATED) as z:
    for row in names:
        for name in row:z.write(SOURCE/(name+'.png'),name+'.png')
    z.write(OUT/'manifest.json','manifest.json')
    if (OUT/'prompts.md').exists():z.write(OUT/'prompts.md','prompts.md')
print(json.dumps({'images':len(records),'contact_sheet':str(OUT/'seis-bases-neutras.png'),'individual_pngs':str(SOURCE)},ensure_ascii=False))
