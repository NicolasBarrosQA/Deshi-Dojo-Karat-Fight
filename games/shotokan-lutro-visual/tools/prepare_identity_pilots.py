"""Mechanically extract authored views and seed inspectable pose attachments.

No drawn faces or synthesized poses: source is the original image_gen PNG.
Run once to create attachment JSON, then retain manual corrections on reruns.
"""
import json
from PIL import Image,ImageFilter,ImageDraw
from pathlib import Path
from character_masks import components
from character_registry import write,read
from compile_character import layer_frames
HERE=Path(__file__).resolve().parents[1]

def unpack(part):
    with Image.open(HERE/'src/assets'/(part['right']+'.png')) as atlas:
        result=[]
        for f in part['frames']:
            im=Image.new('RGBA',(224,144));im.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']));result.append(im)
        return result

def run():
    source=Image.open(HERE/'assets/source/identity-adult-pilots-v1.png').convert('RGBA')
    ids=[('cacheada','Rosto arredondado · cachos curtos'),('franja','Rosto alongado · franja lisa'),('raspado','Rosto quadrado · cabeça raspada'),('preso','Rosto oval · cabelo preso')]
    views=['three_quarter','profile','rear','front'];entries={}
    for row,(key,label) in enumerate(ids):
        entry={'label':label,'views':{},'sizes':{},'pivots':{},'scale':.11,'bald':key=='raspado'}
        extra=Image.open(HERE/'assets/source/identity-adult-pilots-angles-v1.png').convert('RGBA')
        for source_sheet,source_views in [(source,views),(extra,['down','rear_quarter','up','profile_down'])]:
          for col,view in enumerate(source_views):
            cell=source_sheet.crop((col*source_sheet.width//4,row*source_sheet.height//4,(col+1)*source_sheet.width//4,(row+1)*source_sheet.height//4))
            alpha=cell.getchannel('A').point(lambda v:255 if v>=128 else 0)
            group=components(alpha)[0];mask=Image.new('L',cell.size)
            for i in group:mask.putpixel((i%cell.width,i//cell.width),255)
            cell.putalpha(mask);cell=cell.crop(mask.getbbox())
            path=HERE/'assets/source/identities'/f'adult-{key}-{view}.png';path.parent.mkdir(parents=True,exist_ok=True);cell.save(path)
            entry['views'][view]=path.relative_to(HERE).as_posix();entry['sizes'][view]=list(cell.size)
            y=cell.height-4;xs=[x for x in range(cell.width) if cell.getpixel((x,y))[3]]
            entry['pivots'][view]=[round(sum(xs)/len(xs)),cell.height-1]
        entries[key]=entry
        thumbnail=Image.open(HERE/entry['views']['three_quarter']).convert('RGBA')
        thumbnail.thumbnail((40,44),Image.Resampling.NEAREST)
        card=Image.new('RGBA',(48,48));card.paste(thumbnail,((48-thumbnail.width)//2,48-thumbnail.height));card.save(HERE/'src/assets'/f'identity-thumbnail-adult-{key}.png')
    mapping_path=HERE/'assets/identity-adult-attachments.json'
    if not mapping_path.exists():
        masks=read(HERE/'assets/character-masks.json')['adult'];bindings={'base':[]}
        rear={39,42,43,55,57,58,59,60,77,78,79,80}
        for pose in range(1,93):
            r=masks[str(pose)]['head'];view='rear' if pose in rear else 'three_quarter'
            b={'view':view,'anchor':[(r[0]+r[2])//2-2,r[3]-1],'remove':[[r[0],r[1]],[r[2]-1,r[1]],[r[2]-1,r[3]-1],[r[0],r[3]-1]],'occlusion':masks[str(pose)].get('foreground',[])}
            if pose in (85,86):b['angle']=24
            bindings['base'].append(b)
        specials=read(HERE/'assets/special-assets.json')['adult']
        for name,special in specials.items():
            bindings[name]=[]
            for i,im in enumerate(unpack(special['body'])):
                b=im.getbbox();dark=Image.new('L',im.size)
                for y in range(144):
                    for x in range(224):
                        r,g,bl,a=im.getpixel((x,y))
                        if a and max(r,g,bl)<100:dark.putpixel((x,y),255)
                gs=components(dark.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)))
                candidates=[g for g in gs if len(g)>12]
                if name=='knockdown' and i in (4,5):g=min(candidates,key=lambda g:sum(j%224 for j in g)/len(g))
                else:g=min(candidates,key=lambda g:sum(j//224 for j in g)/len(g))
                hr=[min(j%224 for j in g),min(j//224 for j in g),max(j%224 for j in g)+1,max(j//224 for j in g)+1]
                x0,y0,x1,y1=hr;r=[x0-2,y0-2,x1+5,y1+15]
                anchor=[(x0+x1)//2,y1+13];view='three_quarter';angle=0
                if name=='ushiro' and 1<=i<=7 or name=='tai_sabaki' and i in (1,2,5,6) or name=='ura_mawashi' and i in (2,3,4):view='rear'
                if name=='knockdown':
                    if i==1:angle=25
                    if i in (4,5):view='profile';angle=-90;anchor=[x1+12,(y0+y1)//2];r=[x0-2,y0-6,x1+15,y1+2]
                bindings[name].append({'view':view,'anchor':anchor,'angle':angle,'remove':[[r[0],r[1]],[r[2],r[1]],[r[2],r[3]],[r[0],r[3]]]})
        write(mapping_path,bindings)
    write(HERE/'assets/character-identities.json',{'version':1,'source':'assets/source/identity-adult-pilots-v1.png','attachments':{'adult':'assets/identity-adult-attachments.json'},'bodies':{'adult':entries}})
    print('Extracted 32 authored adult head views; attachment JSON preserved if already present.')

if __name__=='__main__':run()
