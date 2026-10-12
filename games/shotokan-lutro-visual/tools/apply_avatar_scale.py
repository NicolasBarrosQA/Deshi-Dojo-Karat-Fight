"""Apply validated scale correction without resetting the user's roster."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];STAGE=ROOT/'.runtime/avatar-set-v3';OUT=ROOT/'docs/avatar-set-v3'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def frame_hash(part,directory):
    f=part['frames'][0];im=Image.open(directory/(part['right']+'.png')).convert('RGBA')
    frame=Image.new('RGBA',(224,144));frame.paste(im.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']))
    return hashlib.sha256(frame.tobytes()).hexdigest()
def main():
    report=read(OUT/'import-report.json');assert not report['missing_sheets'] and not report['quality_errors']
    base=read(STAGE/'character-assets.json');special=read(STAGE/'special-assets.json');assert len(base)==len(special)==6
    old=read(ROOT/'assets/character-assets.json');guards={}
    for body,b in base.items():
        assert len(b['bounds'])==92 and len(special[body])==8
        guards[body]=frame_hash(b['parts']['body']['default'],STAGE/'assets')
        assert guards[body]==frame_hash(old[body]['parts']['body']['default'],ROOT/'src/assets'),(body,'Approved guard changed')
    roster=hashlib.sha256((ROOT/'assets/characters.json').read_bytes()).hexdigest()
    folder=Path.home()/'.codex/backups/deshi-dojo';folder.mkdir(parents=True,exist_ok=True)
    archive=folder/('before-avatar-scale-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'.zip')
    paths=[ROOT/'assets'/name for name in ('character-assets.json','special-assets.json','character-masks.json')]
    paths+=list((ROOT/'src/assets').glob('char-*.png'))+list((ROOT/'src/assets').glob('special-*.png'))
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as backup:
        for p in paths:backup.write(p,p.relative_to(ROOT).as_posix())
    for p in (STAGE/'assets').glob('*.png'):shutil.copy2(p,ROOT/'src/assets'/p.name)
    for name in ('character-assets.json','special-assets.json','character-masks.json'):shutil.copy2(STAGE/name,ROOT/'assets'/name)
    for body in base:
        shutil.copy2(STAGE/(body+'-atlas.png'),ROOT/'docs'/('character-'+body+'-atlas.png'))
        shutil.copy2(STAGE/(body+'-belt-mask.png'),ROOT/'assets'/('character-belt-'+body+'-mask.png'))
    assert roster==hashlib.sha256((ROOT/'assets/characters.json').read_bytes()).hexdigest()
    original=read(ROOT/'assets/import.json');original.update({'sources':report['bodies'],'notes':'Per-pose uniform 2D scale calibrated from upright references and cranial caps; neck area and folded legs do not change body scale.'})
    (ROOT/'assets/import.json').write_text(json.dumps(original,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    result={'approved_guard_hashes':guards,'roster_preserved_sha256':roster,'backup':str(archive),'method':'Upright reference cells set each grounded sheet to its body height; cranial cap calibrates execution and folded airborne poses, excluding exposed neck/chest. A maximum 5% margin adjustment prevents clipping; no runtime scaling or physics changes.','physics_changed':False,'bodies':6,'poses':984}
    (OUT/'scale-correction.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print('Applied scale correction: six approved guards and existing roster unchanged.')
if __name__=='__main__':main()
