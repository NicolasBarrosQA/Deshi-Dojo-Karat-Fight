"""Reimport one repaired original special without touching other staged art."""
import sys,statistics,hashlib
from PIL import Image
from avatar_set_import import ROOT,SOURCE,STAGE,DOCS,BODIES,read,write,figures,skin_head,area,normalize,separate,palettes
from compile_character import pack

def main(group):
    manifest=read(STAGE/'special-assets.json');config=read(ROOT/'assets/characters.json');report=read(DOCS/'import-report.json')
    corrections=read(SOURCE/'corrections.json');occlusions=read(SOURCE/'occlusions.json')
    for body,(_,height) in BODIES.items():
        source=SOURCE/body/(group+'.png');cells=figures(Image.open(source).convert('RGBA'))
        change=corrections.get(body+'/'+group)
        if change:
            fixed=figures(Image.open(SOURCE/change['source']).convert('RGBA'))
            ratio=(area(skin_head(cells[0]))/area(skin_head(fixed[0])))**.5
            for index in change['cells']:
                f=fixed[index];cells[index]=f.resize((round(f.width*ratio),round(f.height*ratio)),Image.Resampling.LANCZOS)
        scale=height/cells[0].height
        frames=[];masks=[];entries=[]
        hidden=occlusions.get(body+'/'+group,{}).get('cells',[])
        for i,cell in enumerate(cells):
            f,m,e=normalize(cell,scale,belt_hidden=i in hidden);frames.append(f);masks.append(m);entries.append(e)
        manifest[body][group]={'body':pack(separate(frames,masks),'special-'+body+'-'+group,STAGE/'assets'),
            'belts':palettes(frames,masks,'special-'+body+'-'+group+'-belt',config,STAGE/'assets'),
            'bounds':[list(f.getbbox()) for f in frames]}
        for row in report['bodies']:
            if row['body']==body:
                for record in row['sheets']:
                    if record['group']==group:
                        record['frames']=entries
                        if change:record['correction_sha256']=hashlib.sha256((SOURCE/change['source']).read_bytes()).hexdigest()
        print('Reimported repaired',body,group,flush=True)
    write(STAGE/'special-assets.json',manifest);write(DOCS/'import-report.json',report)

if __name__=='__main__':main(sys.argv[1])
