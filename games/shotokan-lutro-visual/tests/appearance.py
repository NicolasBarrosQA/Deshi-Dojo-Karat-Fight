"""Generated appearance pixel/pose invariants, independently reconstructed."""
import json,sys,tempfile
from pathlib import Path
from PIL import Image,ImageChops,ImageOps
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE/'tools'))
from character_registry import read,DEFAULT
from compile_character import compile,layer_frames,skin
config=read(HERE/'assets/characters.json');manifest=read(HERE/'assets/character-assets.json');checks=[]
def decode(part,pose,out,side='right'):
    f=part['frames'][pose];source=Image.open(out/(part[side]+'.png'));im=Image.new('RGBA',(224,144))
    im.paste(source.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'] if side=='right' else 224-f['x']-f['w'],f['y']));return im
with tempfile.TemporaryDirectory(prefix='dojo-appearance-') as temp:
    out=Path(temp)
    for body in config['body_order']:
        student={'id':'pixel-test','name':'Pixel Test','body':body,'belt':'amarela','face':'default','hair':'default','appearance':DEFAULT}
        profile=compile(student,out)
        source=[Image.new('RGBA',(224,144)) for _ in range(92)]
        for layer in ('body','face','hair','foreground'):
            for i,f in enumerate(layer_frames(body,layer,'default',manifest)):source[i].alpha_composite(f)
        recolored=compile({**student,'appearance':{**DEFAULT,'skin':'escura'}},out)
        hair_profile=compile({**student,'appearance':{**DEFAULT,'hair_color':'loiro'}},out)
        original_hair=layer_frames(body,'hair','default',manifest)
        belt_sources={belt:layer_frames(body,'belt',belt,manifest) for belt in config['belt_order']}
        changed=0
        for pose,original in enumerate(source):
            generated=decode(profile['parts']['body'],pose,out)
            assert generated.tobytes()==original.tobytes(),(body,pose,'base reconstruction')
            mirrored=decode(profile['parts']['body'],pose,out,'left')
            assert mirrored.tobytes()==ImageOps.mirror(original).tobytes(),(body,pose,'mirror')
            tinted=decode(recolored['parts']['body'],pose,out)
            hair_tinted=decode(hair_profile['parts']['body'],pose,out)
            assert tinted.getchannel('A').tobytes()==original.getchannel('A').tobytes()
            for before,after in zip(original.getdata(),tinted.getdata()):
                if before!=after:
                    assert before[3] and skin(before[:3]),(body,pose,'changed non-skin pixel');changed+=1
            hair_changed=ImageChops.difference(original,hair_tinted).convert('RGB').getbbox()
            if hair_changed:
                for y in range(hair_changed[1],hair_changed[3]):
                    for x in range(hair_changed[0],hair_changed[2]):
                        before,after=original.getpixel((x,y)),hair_tinted.getpixel((x,y))
                        if before!=after:assert original_hair[pose].getpixel((x,y))[3] and not skin(before[:3]) and max(before[:3])>23,(body,pose,'hair recolored skin/gi or fine outline')
            for belt in config['belt_order']:
                actual=decode(profile['parts']['belt'][belt],pose,out)
                expected=belt_sources[belt][pose]
                assert actual.tobytes()==expected.tobytes(),(body,pose,belt,'belt partition')
        assert changed>1000,(body,changed)
        checks.append(f'{body}: all 92 original poses exactly reconstructed/mirrored; 8 exact belt layers; skin changes {changed} only skin pixels, preserves silhouette')
results={'checks':checks,'poses':92*len(config['body_order']),'belt_pose_combinations':92*len(config['body_order'])*len(config['belt_order'])}
(HERE/'docs/appearance-results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
