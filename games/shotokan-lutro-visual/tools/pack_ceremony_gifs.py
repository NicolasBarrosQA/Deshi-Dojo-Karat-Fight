"""Encode screenshots from the shipped game, without synthetic animation."""
import json,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'docs/ceremony'
result={'html_sha256':hashlib.sha256((ROOT/'dist/deshi-dojo-visual.html').read_bytes()).hexdigest(),'gifs':{}}
for name in ('adults','teens','children'):
    paths=sorted((ROOT/'.runtime/hand-touch'/name).glob('*.png'))
    frames=[Image.open(p).convert('RGB').resize((768,448),Image.Resampling.NEAREST).quantize(colors=256,method=Image.Quantize.FASTOCTREE) for p in paths]
    target=out/(name+'.gif')
    temporary=target.with_suffix('.tmp')
    frames[0].save(temporary,format='GIF',save_all=True,append_images=frames[1:],duration=50,loop=0,optimize=True,disposal=1)
    temporary.replace(target)
    with Image.open(target) as encoded:
        assert sum(encoded.seek(i) or encoded.info['duration'] for i in range(encoded.n_frames))==len(frames)*50
        elapsed=0
        for index in range(encoded.n_frames):
            encoded.seek(index);decoded=encoded.convert('RGB').tobytes()
            copies=encoded.info['duration']//50
            for source in frames[elapsed:elapsed+copies]:assert decoded==source.convert('RGB').tobytes(),'GIF delta changed captured pixels'
            elapsed+=copies
        assert elapsed==len(frames)
    result['gifs'][name]={'source_frames':len(paths),'gif_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'screenshots_sha256':hashlib.sha256(b''.join(hashlib.sha256(p.read_bytes()).digest() for p in paths)).hexdigest()}
(out/'gif-results.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS three GIFs encoded from actual offline game screenshots')
