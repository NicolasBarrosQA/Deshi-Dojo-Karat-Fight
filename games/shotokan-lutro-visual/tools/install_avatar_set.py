"""Install the completed authored 2D set; old art is backed up before replacement.

Cleanup is a separately verified PowerShell operation using the saved hashes.
The installer never deletes files and refuses incomplete staged manifests.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, zipfile
from character_registry import DEFAULT

ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/'.runtime/avatar-set-v3'
DOCS=ROOT/'docs/avatar-set-v3'

def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def old_files():
    result=set()
    for p in (ROOT/'src/assets').glob('*.png'):
        if p.stem.startswith(('char-','special-','portrait-','identity-thumbnail-','pose-','fighter-')):result.add(p)
    source=ROOT/'assets/source'
    result.update((source/'avatar-set-v3/references').glob('*.png'))
    for folder in ('female','characters-v2','identities','specials','audit-corrections','avatar-rig-pilot'):
        result.update(p for p in (source/folder).rglob('*') if p.is_file())
    for p in source.glob('*.png'):
        if p.name!='dojo.png':result.add(p)
    for p in (ROOT/'docs').glob('*'):
        if p.is_file() and (p.name.startswith(('character-','identity-','scene-')) or p.suffix=='.gif'):result.add(p)
    for folder in ('female-bodies','pose-audit','identity-audit','identity-pilots','special-captures','avatar-rig-pilot'):
        result.update(p for p in (ROOT/'docs'/folder).rglob('*') if p.is_file())
    for name in ('characters.json','character-assets.json','character-masks.json','character-visuals.json',
                 'special-assets.json','special-profiles.json','character-identities.json','identity-adult-attachments.json',
                 'female-existing-art-baseline.json','character-source-layout.json','character-belt-overrides.json',
                 'character-import.json','character-provenance.json','character-provenance-v2.json','import.json'):
        p=ROOT/'assets'/name
        if p.exists():result.add(p)
    result.update((ROOT/'assets').glob('character-belt-*-mask.png'))
    for name in ('art.lua','character_data.lua'):
        result.add(ROOT/'src'/name)
    pilot=ROOT/'tools/build_avatar_rig.py'
    if pilot.exists():result.add(pilot)
    for p in (ROOT/'dist').glob('*'):
        if p.is_file() and p.suffix in ('.html','.lutro','.zip'):result.add(p)
    return sorted(result)

def backup():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    folder=Path.home()/'.codex/backups/deshi-dojo';folder.mkdir(parents=True,exist_ok=True)
    target=folder/('characters-before-neutral-2d-'+stamp+'.zip')
    files=old_files();entries=[]
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
        for i,p in enumerate(files):
            if not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Backup file escaped game root')
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            relative=p.relative_to(ROOT).as_posix()
            obsolete={'identity-adult-attachments.json','female-existing-art-baseline.json','character-source-layout.json','character-belt-overrides.json','character-provenance.json','character-provenance-v2.json'}
            cleanup=(relative.startswith('assets/source/') or relative.startswith('docs/') or relative=='tools/build_avatar_rig.py' or relative.startswith('src/assets/') or p.name in obsolete or relative.startswith('dist/') and p.suffix=='.zip')
            archive.write(p,relative);entries.append({'path':str(p.resolve()),'sha256':digest,'cleanup_candidate':cleanup})
            if i%300==0:print('Backed up',i,'/',len(files),flush=True)
    write(DOCS/'legacy-art-backup.json',{'archive':str(target),'game_root':str(ROOT.resolve()),'files':entries})
    print('Backup saved',target,flush=True)

def install():
    report=read(DOCS/'import-report.json')
    assert not report['missing_sheets'],'Incomplete source art'
    assert not report.get('quality_errors'),'Source art repairs still required'
    base=read(STAGE/'character-assets.json');special=read(STAGE/'special-assets.json')
    assert len(base)==len(special)==6
    for body,a in base.items():
        assert len(a['bounds'])==92 and len(special[body])==8
        for s in special[body].values():assert len(s['bounds'])==9
    backup()
    for p in (STAGE/'assets').glob('*.png'):shutil.copy2(p,ROOT/'src/assets'/p.name)
    for name in ('character-assets.json','special-assets.json','character-masks.json'):
        shutil.copy2(STAGE/name,ROOT/'assets'/name)
    for body in base:
        shutil.copy2(STAGE/(body+'-atlas.png'),ROOT/'docs'/('character-'+body+'-atlas.png'))
        shutil.copy2(STAGE/(body+'-belt-mask.png'),ROOT/'assets'/('character-belt-'+body+'-mask.png'))
    config=read(ROOT/'assets/characters.json')
    names={'adult':('demo-adult','Adulto Masculino'), 'teen':('demo-teen','Adolescente Masculino'),
           'child':('demo-child','Crianca Masculina'), 'adult_female':('demo-adult-female','Adulta Feminina'),
           'teen_female':('demo-teen-female','Adolescente Feminina'), 'child_female':('demo-child-female','Crianca Feminina')}
    config['body_order']=list(names)
    config['students']={ident:{'id':ident,'name':name,'nickname':'Base neutra 2D','body':body,
        'belt':'branca','face':'default','hair':'default','appearance':DEFAULT.copy()} for body,(ident,name) in names.items()}
    config['student_order']=list(config['students'])
    write(ROOT/'assets/characters.json',config)
    write(ROOT/'assets/character-identities.json',{'version':3,'attachments':{},'bodies':{},'note':'Six approved neutral 2D bases; legacy heads removed by user request.'})
    for name in ('character-visuals.json','special-profiles.json'):write(ROOT/'assets'/name,{})
    # Import metadata now describes actual new sources; physics pose bounds stay
    # unchanged because replacing illustrations does not rebalance combat.
    original=read(ROOT/'assets/import.json')
    original.update({'revision':'neutral-2d-v3','sources':report['bodies'],'notes':'Original 2D art, chroma cloth masks, head-calibrated sheet scale. Six bases replace old fighters; existing combat bounds unchanged.'})
    write(ROOT/'assets/import.json',original)
    write(ROOT/'assets/character-import.json',{'poses':92,'revision':'neutral-2d-v3','bases':{k:{'frames':92,'bounds':v['bounds']} for k,v in base.items()}})
    write(DOCS/'installed.json',{'bodies':list(base),'poses':984,'roster':list(config['students']),'legacy_cleanup_pending':True,'physics_changed':False})
    print('Installed six neutral 2D bodies and all 984 poses. Build/test before legacy cleanup.',flush=True)

if __name__=='__main__':install()
