"""Import separately authored turnarounds; never manufacture cuts by tinting."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
from character_registry import read,write
from import_hair import VIEWS,REGISTRATION

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/source/hair-catalog-v1'

def extract(path,ident,category):
    with Image.open(path) as im:sheet=im.convert('RGBA')
    if sheet.width%3 or sheet.height%2:raise ValueError(f'Invalid six-view grid: {path}')
    cw,ch=sheet.width//3,sheet.height//2;views={}
    for i,view in enumerate(VIEWS):
        cell=sheet.crop((i%3*cw,i//3*ch,(i%3+1)*cw,(i//3+1)*ch))
        p=np.asarray(cell).copy();r,g,b,a=[p[:,:,c].astype(float) for c in range(4)]
        material=(a>0)&(r>g*1.08)&(g>b*1.03)&(r-b>9)
        grow=np.asarray(Image.fromarray((material*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)))>0
        ink=(np.maximum.reduce([r,g,b])<80)&(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])<38)
        visible=material|(grow&ink)
        if category=='barba' and view in ('rear','top'):visible[:]=False
        if category!='barba' and np.count_nonzero(visible)<200:raise ValueError(f'Empty hair view: {ident}/{view}')
        p[:,:,3]=visible*255;p[~visible]=0
        target=SOURCE/(ident+'-'+view+'.png');Image.fromarray(p).save(target)
        pivot,width,height=REGISTRATION[i]
        views[view]={'path':target.relative_to(ROOT).as_posix(),'center':[pivot[0]*cw/512,pivot[1]*ch/512],'width':width*cw/512,'height':height*ch/512}
    return views

def main(partial=False):
    plan=read(SOURCE/'production-plan.json');hair=read(ROOT/'assets/hair-assets.json')
    for value in hair['styles'].values():value.setdefault('category','masculino')
    beard={'version':1,'styles':{}};missing=[];hashes=set()
    for entry in plan['entries']:
        ident=entry['id'];path=SOURCE/(ident+'-views.png')
        if not path.exists():missing.append(ident);continue
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in hashes:raise ValueError(f'Duplicate authored source: {ident}')
        hashes.add(digest)
        record={'label':entry['label'],'category':entry['category'],'brief':entry['brief'],'source_sha256':digest,'views':extract(path,ident,entry['category'])}
        (beard if entry['category']=='barba' else hair)['styles'][ident]=record
    if missing and not partial:raise ValueError('Production not complete: '+', '.join(missing))
    hair['version']=3
    write(ROOT/'assets/hair-assets.json',hair);write(ROOT/'assets/beard-assets.json',beard)
    from prepare_hair_bindings import animations
    from hair_art import apply,PAD
    poses=animations();thumbs=SOURCE/'thumbnails';thumbs.mkdir(exist_ok=True)
    for kind,catalog in [('hair',hair),('beard',beard)]:
        for ident,entry in catalog['styles'].items():
            body='adult_female' if entry.get('category')=='feminino' else 'adult'
            student={'body':body,'hair':ident if kind=='hair' else 'default','beard':ident if kind=='beard' else 'default','appearance':{'hair_color':'original'}}
            frame=apply(poses[body]['base'][0],student,'base',0)
            crop=frame.crop((86,PAD,142,PAD+56)).resize((112,112),Image.Resampling.NEAREST)
            crop.save(thumbs/((ident if kind=='hair' else 'beard-'+ident)+'.png'))
    print(json.dumps({'hair':len(hair['styles']),'beards':len(beard['styles']),'missing':missing}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--partial',action='store_true');args=parser.parse_args();main(args.partial)
