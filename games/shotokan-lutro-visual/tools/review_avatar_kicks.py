"""Source-art contact sheet for manual limb/direction audit, not gameplay."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from avatar_set_import import ROOT,SOURCE,BODIES,figures
poses=[27,31,35,51,55,59,67,75,79,83]
out=ROOT/'docs/avatar-set-v3';font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
canvas=Image.new('RGB',(300*len(poses),340*6),'#e6e8ee')
for row,body in enumerate(BODIES):
    cache={}
    for col,pose in enumerate(poses):
        group=f'base-{((pose-1)//9)*9+1:02d}'
        if group not in cache:cache[group]=figures(Image.open(SOURCE/body/(group+'.png')).convert('RGBA'))
        im=cache[group][(pose-1)%9].copy();im.thumbnail((286,286),Image.Resampling.LANCZOS)
        canvas.paste(im,(300*col+(300-im.width)//2,340*row+45+(286-im.height)//2),im)
        ImageDraw.Draw(canvas).text((300*col+3,340*row+4),body+' #'+str(pose),font=font,fill='#172033')
canvas.save(out/'source-kicks-review.png')
print('Source kick review: 60 original full-extension poses, before corrections; presentation sizes only.')
