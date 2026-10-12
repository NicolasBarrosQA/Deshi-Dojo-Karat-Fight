"""Adjust quad placement only; preserve authored pixels, scale and physics."""
from pathlib import Path
from datetime import datetime,timezone
import json,zipfile,shutil
from PIL import Image
from avatar_set_import import jump_cap_center
ROOT=Path(__file__).resolve().parents[1];STAGE=ROOT/'.runtime/avatar-set-v3';OUT=ROOT/'docs/avatar-set-v3'
def read(path):return json.loads(path.read_text(encoding='utf8'))
def write(path,data):path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def move_box(box,dx):
    if box:box[0]+=dx;box[2]+=dx
def sync_metadata(base,report):
    path=ROOT/'assets/character-import.json';data=read(path)
    for body,b in base.items():data['bases'][body]['bounds']=b['bounds']
    write(path,data)
    path=ROOT/'assets/import.json';data=read(path);data['sources']=report['bodies'];write(path,data)
def shift_atlas(path,dx):
    im=Image.open(path);x=(62%4)*224;y=(62//4)*144;cell=im.crop((x,y,x+224,y+144))
    moved=Image.new(im.mode,cell.size);moved.paste(cell,(dx,0));im.paste(moved,(x,y));im.save(path)
def unpack(part,index):
    f=part['frames'][index];im=Image.open(ROOT/'src/assets'/(part['right']+'.png')).convert('RGBA')
    frame=Image.new('RGBA',(224,144));frame.paste(im.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']));return frame
def main():
    base=read(ROOT/'assets/character-assets.json');masks=read(ROOT/'assets/character-masks.json')
    report=read(OUT/'import-report.json');changes=[]
    if all(b.get('jump_anchor',{}).get('metric')=='cranial-cap-v2' for b in base.values()):
        print('All six descent anchors already aligned; existing audit preserved.');return
    backup=Path.home()/'.codex/backups/deshi-dojo'/('before-jump-anchor-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'.zip');backup.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
        for path in [ROOT/'assets/character-assets.json',ROOT/'assets/character-masks.json',OUT/'import-report.json']:
            z.write(path,path.relative_to(ROOT).as_posix())
    for body,b in base.items():
        if b.get('jump_anchor',{}).get('metric')=='cranial-cap-v2':continue
        part=b['parts']['body']['default'];first=jump_cap_center(unpack(part,61));second=jump_cap_center(unpack(part,62))
        dx=round(first-second);total_dx=b.get('jump_anchor',{}).get('descent_offset_x',0)+dx
        assert 0<=b['bounds'][62][0]+dx<b['bounds'][62][2]+dx<=224
        for layer,variants in b['parts'].items():
            for part in variants.values():
                f=part['frames'][62]
                if f['w']>1 or f['h']>1:f['x']+=dx
        move_box(b['bounds'][62],dx)
        for key in ('head','belt'):move_box(masks[body]['63'][key],dx)
        b['jump_anchor']={'poses':[62,63],'descent_offset_x':total_dx,'metric':'cranial-cap-v2','rise_anchor_x':first,'descent_anchor_x':second+dx,'reference':'Cranial cap centre, excluding angled neck, across rise and descent; facing mirror applies normally.'}
        masks[body]['62']['jump_cap_x']=first;masks[body]['63']['jump_cap_x']=second+dx
        for row in report['bodies']:
            if row['body']==body:
                entry=next(s for s in row['sheets'] if s['group']=='base-55')['frames'][8]
                for key in ('head','belt','bounds'):move_box(entry[key],dx)
                entry['jump_transition_shift_x']=total_dx;entry['jump_cap_x']=second+dx
                next(s for s in row['sheets'] if s['group']=='base-55')['frames'][7]['jump_cap_x']=first
        for p in [ROOT/'docs'/('character-'+body+'-atlas.png'),ROOT/'assets'/('character-belt-'+body+'-mask.png'),STAGE/(body+'-atlas.png'),STAGE/(body+'-belt-mask.png')]:shift_atlas(p,dx)
        changes.append({'body':body,'pose':63,'shift_x':dx,'total_shift_from_original_x':total_dx})
    for directory in (ROOT/'assets',STAGE):
        write(directory/'character-assets.json',base);write(directory/'character-masks.json',masks)
    write(OUT/'import-report.json',report)
    sync_metadata(base,report)
    write(OUT/'jump-anchor-correction.json',{'changes':changes,'backup':str(backup),'pixels_and_scale_unchanged':True,'physics_changed':False,'purpose':'Remove the visible upper-body jump at the rise-to-descent transition, including mirrored P2.'})
    print('Aligned descent quad placement:',changes)
if __name__=='__main__':main()
