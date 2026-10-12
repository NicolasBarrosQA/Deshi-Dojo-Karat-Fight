"""Prepare explicit, reviewable scalp attachments from the approved bald poses."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw
from head_registration import measure,runs,beard_foreground

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

def prepare():
    overrides_path=ROOT/'assets/hair-binding-overrides.json'
    overrides=json.loads(overrides_path.read_text()) if overrides_path.exists() else {}
    result={};beard_result={};docs=ROOT/'docs/hair';docs.mkdir(parents=True,exist_ok=True)
    for body,entries in animations().items():
        result[body]={};beard_result[body]={};crops=[]
        for group,frames in entries.items():
            result[body][group]=[];beard_result[body][group]=[]
            for index,im in enumerate(frames):
                key=f'{group}:{index+1}';change=overrides.get(body,{}).get(key,{})
                floor=group=='knockdown' and 5<=index+1<=7
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
                registration,foreground=measure(im,angle)
                binding={**registration,'view':view,'foreground_runs':runs(foreground),'registration':'cranial-oval-v2'}
                # Reviewed overrides are applied to the final cranial measurement,
                # never to a component that can include the supporting forearm.
                binding.update(change);beard_result[body][group].append(runs(beard_foreground(im,binding)));result[body][group].append(binding)
                cx,cy=binding['center']
                crop=im.crop((max(0,round(cx)-30),max(0,round(cy)-30),min(224,round(cx)+30),min(144,round(cy)+35)))
                crops.append((key,crop))
        sheet=Image.new('RGB',(120*14,155*math.ceil(len(crops)/14)),'#344651');draw=ImageDraw.Draw(sheet)
        for i,(key,crop) in enumerate(crops):
            x=i%14*120;y=i//14*155;crop=crop.resize((crop.width*2,crop.height*2),Image.Resampling.NEAREST);sheet.paste(crop,(x,y+20),crop);draw.text((x+2,y+3),key,fill='white')
        sheet.save(docs/(body+'-heads-before.png'));print(body,len(crops),'cranial registrations',flush=True)
    from character_registry import write
    write(ROOT/'assets/hair-bindings.json',result)
    target=ROOT/'assets/beard-bindings.json';temp=target.with_suffix('.json.tmp');temp.write_text(json.dumps(beard_result,separators=(',',':'))+'\n');temp.replace(target)

if __name__=='__main__':prepare()
