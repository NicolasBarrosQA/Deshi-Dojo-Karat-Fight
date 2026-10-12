"""Validate historical ZIP paths/assets and their manifest without dependencies."""
from pathlib import Path
import hashlib,json,struct,zipfile
HERE=Path(__file__).resolve().parents[1]
manifest=json.loads((HERE/'assets/character-assets.json').read_text())
with zipfile.ZipFile(HERE/'dist/deshi-dojo-visual.lutro') as cart:
    names=cart.namelist();assert names[0]=='assets/'
    assert not any('\\' in name for name in names),'Windows separators in cartridge'
    for module in ('main.lua','conf.lua','characters.lua','character_data.lua','art.lua','cpu.lua','techniques.lua','motion.lua','specials.lua','ceremony.lua'):
        assert module in names
    roster=json.loads((HERE/'assets/characters.json').read_text(encoding='utf-8'))
    visual_path=HERE/'assets/character-visuals.json'
    profiles=json.loads(visual_path.read_text()) if visual_path.exists() else {}
    active={student['visual'] for student in roster['students'].values() if student.get('visual')}
    for key in active:
        profile=profiles[key]
        for part in [profile['parts']['body'],*profile['parts']['belt'].values()]:
            assert len(part['frames'])==92
            for side in ('left','right'):
                raw=cart.read('assets/'+part[side]+'.png')
                assert struct.unpack('>II',raw[16:24])==(part['width'],part['height'])
            for f in part['frames']:
                assert f['sx']>=0 and f['sy']>=0 and f['sx']+f['w']<=part['width'] and f['sy']+f['h']<=part['height']
        assert 'assets/'+profile['portrait']+'.png' in names
    for body in manifest.values():
        for variants in body['parts'].values():
            for part in variants.values():
                assert len(part['frames'])==92
                for side in ('left','right'):
                    name='assets/'+part[side]+'.png';raw=cart.read(name)
                    assert raw[:8]==b'\x89PNG\r\n\x1a\n'
                    assert struct.unpack('>II',raw[16:24])==(part['width'],part['height'])
                    assert raw==(HERE/'src'/name).read_bytes()
    specials=json.loads((HERE/'assets/special-assets.json').read_text())
    for body,animation in json.loads((HERE/'assets/ceremony-assets.json').read_text()).items():specials[body]['ceremony']=animation
    for body,animation in json.loads((HERE/'assets/hand-touch-assets.json').read_text()).items():specials[body]['hand_touch']=animation
    for groups in specials.values():
        for animation in groups.values():
            for part in [animation['body'],*animation['belts'].values()]:
                assert len(part['frames'])==9
                for side in ('left','right'):
                    raw=cart.read('assets/'+part[side]+'.png')
                    assert struct.unpack('>II',raw[16:24])==(part['width'],part['height'])
    for sound in ('sweep','ground','finish'):
        assert cart.read('assets/special-'+sound+'.wav')[:4]==b'RIFF'
    for line in (HERE/'dist/SHA256SUMS.txt').read_text().splitlines():
        sha,name=line.split();assert hashlib.sha256((HERE/'dist'/name).read_bytes()).hexdigest()==sha
print('PASS cart includes modules and every part with correct PNG dimensions, portable ZIP paths and matching SHA-256')
