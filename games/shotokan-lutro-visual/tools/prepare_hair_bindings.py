"""Prepare explicit, reviewable scalp attachments from the approved bald poses."""
import json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from avatar_set_import import groups,box,area

ROOT=Path(__file__).resolve().parents[1]

def unpack(part):
    with Image.open(ROOT/'src/assets'/(part['right']+'.png')) as source:
        result=[]
        for f in part['frames']:
            im=Image.new('RGBA',(224,144));im.paste(source.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']));result.append(im)
        return result

def animations():
    base=json.loads((ROOT/'assets/character-assets.json').read_text());result={b:{'base':unpack(v['parts']['body']['default'])} for b,v in base.items()}
    for file in ('special-assets.json','ceremony-assets.json','hand-touch-assets.json'):
        data=json.loads((ROOT/'assets'/file).read_text())
        for body,value in data.items():
            entries=value if file=='special-assets.json' else {('ceremony' if file=='ceremony-assets.json' else 'hand_touch'):value}
            for name,entry in entries.items():result[body][name]=unpack(entry['body'])
    return result

def component(im,hint=None,floor=False):
    p=np.asarray(im).astype(float);r,g,b,a=[p[:,:,i] for i in range(4)]
    candidates=[v for v in groups((a>0)&(r>55)&(r>g*1.055)&(g>b*1.015)&(r-b>16)) if area(v)>=35]
    if not candidates:raise ValueError('Missing scalp component')
    if floor:return max(candidates,key=lambda v:area(v)-box(v)[0]*1.5)
    if hint:
        return min(candidates,key=lambda v:abs(box(v)[1]-hint[1])*3+abs((box(v)[0]+box(v)[2]-hint[0]-hint[2])/2))
    return min(candidates,key=lambda v:box(v)[1]+max(0,65-area(v))*.3)

def prepare():
    masks=json.loads((ROOT/'assets/character-masks.json').read_text());overrides_path=ROOT/'assets/hair-binding-overrides.json'
    overrides=json.loads(overrides_path.read_text()) if overrides_path.exists() else {}
    result={};docs=ROOT/'docs/hair';docs.mkdir(parents=True,exist_ok=True)
    for body,entries in animations().items():
        reference=[]
        for i,im in enumerate(entries['base'][:6]):
            v=component(im,masks[body][str(i+1)]['head']);t=box(v)[1]
            widths=[e-s for y,s,e in v if t+3<=y<t+12];reference.append(max(widths))
        width=float(np.median(reference));result[body]={};crops=[]
        for group,frames in entries.items():
            result[body][group]=[]
            for index,im in enumerate(frames):
                key=f'{group}:{index+1}';change=overrides.get(body,{}).get(key,{})
                floor=group=='knockdown' and 5<=index+1<=7
                hint=masks[body][str(index+1)]['head'] if group=='base' and index+1 not in (59,) else None
                v=component(im,hint,floor);bounds=box(v);left,top,right,bottom=bounds
                view='three_quarter';angle=0
                if group=='base' and index+1 in (9,42,43,57,58,59,60,81,82,83):view='rear_three_quarter'
                if group=='base' and index+1 in (85,86):angle=55
                if group=='ushiro' and index+1 in (2,4,5,6):view='rear_three_quarter'
                if group=='ura_mawashi' and index+1 in (2,3):view='rear_three_quarter'
                if group=='knockdown' and index+1 in (3,4):angle=25 if index+1==3 else 50
                if group=='tai_sabaki' and index+1==3:view='rear_three_quarter'
                if group=='ceremony' and index+1 in (2,3,4):angle=-25 if index+1==3 else -12
                if floor:
                    angle=90 if index+1 in (5,6) else 35
                    cx=left+width*.55;cy=(top+bottom)/2 if index+1 in (5,6) else top+width*.50
                else:
                    upper=[(y,s,e) for y,s,e in v if top+2<=y<top+min(13,width*.65)]
                    widest=sorted(upper,key=lambda row:row[2]-row[1],reverse=True)[:4]
                    cx=float(np.median([(s+e-1)/2 for y,s,e in widest]));cy=top+width*.6
                measured=width if floor or abs(angle)>=45 else max(width*.8,min(width*1.25,float(np.median([e-s for y,s,e in widest]))))
                binding={'center':[round(cx,2),round(cy,2)],'width':round(measured,2),'view':view,'angle':angle,'head_component':list(bounds)}
                p=np.asarray(im).astype(float);r,g,b,a=[p[:,:,c] for c in range(4)]
                others=groups((a>0)&(r>55)&(r>g*1.055)&(g>b*1.015)&(r-b>16))
                occlusion=[]
                for part in others:
                    if part==v:continue
                    for y,s,e in part:
                        if abs(y-cy)<width*1.2 and s<cx+width and e>cx-width:occlusion.append([y,s,e])
                if occlusion:binding['foreground_runs']=occlusion
                binding.update(change);result[body][group].append(binding)
                crop=im.crop((max(0,round(cx)-30),max(0,round(cy)-30),min(224,round(cx)+30),min(144,round(cy)+35)))
                crops.append((key,crop))
        sheet=Image.new('RGB',(120*14,155*math.ceil(len(crops)/14)),'#344651');draw=ImageDraw.Draw(sheet)
        for i,(key,crop) in enumerate(crops):
            x=i%14*120;y=i//14*155;crop=crop.resize((crop.width*2,crop.height*2),Image.Resampling.NEAREST);sheet.paste(crop,(x,y+20),crop);draw.text((x+2,y+3),key,fill='white')
        sheet.save(docs/(body+'-heads-before.png'));print(body,len(crops),'head width',width,flush=True)
    from character_registry import write
    write(ROOT/'assets/hair-bindings.json',result)

if __name__=='__main__':prepare()
