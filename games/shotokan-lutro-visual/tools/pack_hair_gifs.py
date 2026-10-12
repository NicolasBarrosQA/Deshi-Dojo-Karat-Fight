"""Package actual exported-game captures; verify decoded GIFs match screenshots."""
from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'docs/hair';reports={}
for name in ('adult','teen','child'):
    paths=sorted((ROOT/'.runtime/hair-captures'/name).glob('*.png'));assert len(paths)==187
    frames=[Image.open(p).convert('RGB').resize((768,448),Image.Resampling.NEAREST).quantize(colors=256,method=Image.Quantize.FASTOCTREE) for p in paths]
    target=out/(name+'-runtime.gif');temporary=target.with_suffix('.tmp')
    frames[0].save(temporary,format='GIF',save_all=True,append_images=frames[1:],duration=50,loop=0,optimize=True,disposal=1);temporary.replace(target)
    with Image.open(target) as encoded:
        elapsed=0
        for i in range(encoded.n_frames):
            encoded.seek(i);copies=encoded.info['duration']//50;decoded=encoded.convert('RGB').tobytes()
            for source in frames[elapsed:elapsed+copies]:assert decoded==source.convert('RGB').tobytes()
            elapsed+=copies
        assert elapsed==len(frames)
    reports[name]={'source_frames':len(paths),'milliseconds':len(paths)*50,'gif_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'capture_sha256':hashlib.sha256(b''.join(hashlib.sha256(p.read_bytes()).digest() for p in paths)).hexdigest(),'source':'Actual offline export generated in isolated hair_creator fixture; live roster preserved.'}
(out/'gif-results.json').write_text(json.dumps(reports,indent=2)+'\n');print('PASS actual hair runtime GIFs, all decoded pixels verified')
