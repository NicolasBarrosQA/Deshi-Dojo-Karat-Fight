"""Arrange actual browser captures at integer pixel zoom for visual QA."""
from PIL import Image,ImageDraw
from import_characters import HERE
out=Image.new('RGB',(768,3*472),'#0d151b');d=ImageDraw.Draw(out)
for row,(body,label) in enumerate([('adult','ADULTO'),('teen','ADOLESCENTE'),('child','CRIANCA')]):
    d.text((8,row*472+5),label+' - P1 saltando / P2 em pe',fill='white')
    im=Image.open(HERE/'docs'/f'jump-{body}-62.png').convert('RGB')
    out.paste(im.resize((768,448),Image.Resampling.NEAREST),(0,row*472+24))
out.save(HERE/'docs/jump-scale-browser-review.png')
