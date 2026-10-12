"""Review exact staged/installed drawable poses, including canonical guards."""
import argparse
from PIL import Image,ImageDraw,ImageFont
from avatar_set_import import ROOT,STAGE,DOCS,BODIES,read

def main(installed=False):
    directory=ROOT/'assets' if installed else STAGE
    assets=ROOT/'src/assets' if installed else STAGE/'assets'
    base=read(directory/'character-assets.json');special=read(directory/'special-assets.json')
    cache={};font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
    def frame(part,i):
        if part['right'] not in cache:cache[part['right']]=Image.open(assets/(part['right']+'.png')).convert('RGBA')
        f=part['frames'][i];out=Image.new('RGBA',(224,144));out.paste(cache[part['right']].crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']));return out
    full={}
    for body,b in base.items():
        full[body]={'base':[]}
        for i in range(92):
            out=Image.new('RGBA',(224,144))
            for layer in ('body','face','hair','foreground'):out.alpha_composite(frame(b['parts'][layer]['default'],i))
            out.alpha_composite(frame(b['parts']['belt']['branca'],i));full[body]['base'].append(out)
        for group,a in special[body].items():full[body][group]=[Image.alpha_composite(frame(a['body'],i),frame(a['belts']['branca'],i)) for i in range(9)]
    for group,start in [('base',i) for i in range(0,92,9)]+[(g,0) for g in next(iter(special.values()))]:
        name=f'base-{start+1:02d}' if group=='base' else group
        sheet=Image.new('RGB',(2016,1080),'#e6e8ee')
        for row,body in enumerate(BODIES):
            ImageDraw.Draw(sheet).text((4,row*180+2),body+' / '+name,font=font,fill='#172033')
            for col,f in enumerate(full[body][group][start:start+9]):sheet.paste(f,(224*col,row*180+30),f)
        sheet.resize((4032,2160),Image.Resampling.NEAREST).save(DOCS/(name+'-review.png'))
    print('Updated 19 exact runtime review pages, all 984 slots.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--installed',action='store_true');a=p.parse_args();main(a.installed)
