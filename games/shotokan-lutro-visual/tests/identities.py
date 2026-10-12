"""Identity integration: original limbs/belts, all poses, mirrors and cache inputs."""
import sys,json,hashlib,tempfile,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageChops
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE/'tools'))
from character_registry import read,validate,visual_key,DEFAULT
from compile_character import layer_frames,transform
from identity_art import catalog,attachments,head,fingerprint
from prepare_identity_pilots import unpack

config=read(HERE/'assets/characters.json');manifest=read(HERE/'assets/character-assets.json');profiles=read(HERE/'assets/character-visuals.json');specials=read(HERE/'assets/special-assets.json');special_profiles=read(HERE/'assets/special-profiles.json')
checks=[];count=0;belts=0;signatures=[];silhouettes=[]
base=[Image.new('RGBA',(224,144)) for _ in range(92)]
for layer in ('body','face','hair','foreground'):
    for i,f in enumerate(layer_frames('adult',layer,'default',manifest)):base[i].alpha_composite(f)

decoded={}
def decode(part,side='right'):
    name=part[side]
    if name in decoded:return decoded[name]
    with Image.open(HERE/'src/assets'/(part[side]+'.png')) as atlas:
        frames=[]
        for f in part['frames']:
            im=Image.new('RGBA',(224,144));x=f['x'] if side=='right' else 224-f['x']-f['w']
            im.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(x,f['y']));frames.append(im)
        decoded[name]=frames;return frames

for identity,entry in catalog()['bodies']['adult'].items():
    student=config['students']['pilot-adult-'+identity];key=visual_key(student);profile=profiles[key]
    assert len(entry['views'])==8 and profile['identity']==identity and special_profiles[key]['identity']==identity
    signatures.append(hashlib.sha256(decode(profile['parts']['body'])[0].tobytes()).hexdigest())
    silhouettes.append(hashlib.sha256(decode(profile['parts']['body'])[0].getchannel('A').tobytes()).hexdigest())
    assert key==visual_key({**student,'name':'Outro nome','id':'outro-id','belt':'amarela'})
    for invalid in ({**student,'body':'child'},{**student,'identity':'missing'},{**student,'face':'missing'}):
        try:validate(invalid,config,manifest)
        except ValueError:pass
        else:raise AssertionError('Invalid identity accepted')
    actual_groups={'base':profile['parts']['body'],**{g:p['body'] for g,p in special_profiles[key]['groups'].items()}}
    for group,part in actual_groups.items():
        right=decode(part);left=decode(part,'left');originals=base if group=='base' else unpack(specials['adult'][group]['body']);bindings=attachments('adult',group)
        assert len(right)==len(bindings)==(92 if group=='base' else 9)
        for i,(before,after) in enumerate(zip(originals,right)):
            assert set(after.getchannel('A').tobytes())<={0,255}
            assert left[i].tobytes()==ImageOps.mirror(after).tobytes(),(identity,group,i,'mirror')
            changed=ImageChops.difference(before,after).convert('RGB').getbbox();assert changed,(identity,group,i,'identity did not appear')
            allowed=Image.new('L',(224,144));ImageDraw.Draw(allowed).polygon([tuple(p) for p in bindings[i]['remove']],fill=255)
            new_head=head(student,bindings[i]);allowed=ImageChops.lighter(allowed,new_head.getchannel('A'))
            diff=ImageChops.difference(before,after);r,g,b,a=diff.split();visible=ImageChops.lighter(before.getchannel('A'),after.getchannel('A'))
            rgb_difference=ImageChops.multiply(ImageChops.lighter(ImageChops.lighter(r,g),b),visible)
            maximum=ImageChops.lighter(rgb_difference,a)
            assert ImageChops.multiply(maximum,ImageOps.invert(allowed)).getbbox() is None,(identity,group,i,'changed outside head')
            if group=='base' and i==14:
                for rect in bindings[i]['occlusion']:
                    old,new=before.crop(rect),after.crop(rect);delta=ImageChops.difference(old,new);r,g,b,a=delta.split()
                    difference=ImageChops.lighter(ImageChops.lighter(r,g),ImageChops.lighter(b,a))
                    assert ImageChops.multiply(difference,old.getchannel('A')).getbbox() is None,'High-block arm was hidden'
            if group=='knockdown' and i in (4,5):assert new_head.getbbox()[3]<=143,'Head crossed floor'
            for height in (.94,1,1.04):
                for build in ('leve','medio','forte'):transform(after,{**DEFAULT,'height':height,'build':build},(manifest['adult']['bounds'] if group=='base' else specials['adult'][group]['bounds'])[i])
            count+=1
        choices=profile['parts']['belt'] if group=='base' else special_profiles[key]['groups'][group]['belts']
        originals_belts=manifest['adult']['parts']['belt'] if group=='base' else specials['adult'][group]['belts']
        for belt,record in choices.items():
            for before,after in zip(decode(originals_belts[belt]),decode(record)):
                assert before.tobytes()==after.tobytes(),(identity,group,belt,'belt changed');belts+=1
    checks.append(identity+': 164 poses, both directions, head-only changes, 8 intact belt layers, 9 height/build combinations')
assert len(set(signatures))==4,'Identity options are duplicate recolors'
assert len(set(silhouettes))==4,'Identity options must have different authored silhouettes'
# Verify authored-resource edits invalidate the identity digest in a temporary copy.
import identity_art
with tempfile.TemporaryDirectory() as tmp:
    task_root=Path(tmp);shutil.copytree(HERE/'assets',task_root/'assets',ignore=shutil.ignore_patterns('*.png'))
    shutil.copytree(HERE/'assets/source/identities',task_root/'assets/source/identities',dirs_exist_ok=True)
    previous_root,previous_catalog=identity_art.HERE,identity_art.CATALOG
    try:
        identity_art.HERE=task_root;identity_art.CATALOG=task_root/'assets/character-identities.json'
        shutil.copytree(HERE/'tools',task_root/'tools',ignore=shutil.ignore_patterns('__pycache__'))
        student=config['students']['pilot-adult-cacheada'];before=fingerprint(student)
        asset=task_root/catalog()['bodies']['adult']['cacheada']['views']['three_quarter'];asset.write_bytes(asset.read_bytes()+b'cache-test')
        assert fingerprint(student)!=before
    finally:identity_art.HERE=previous_root;identity_art.CATALOG=previous_catalog
result={'poses':count,'belt_pose_combinations':belts,'checks':checks,'native_hardware_tested':False}
(HERE/'docs/identity-pilots/test-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
