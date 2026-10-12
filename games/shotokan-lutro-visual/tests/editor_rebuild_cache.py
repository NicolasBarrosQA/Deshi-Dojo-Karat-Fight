"""Derived visual timestamps must not cause perpetual local game rebuilds."""
from pathlib import Path
import tempfile,importlib.util,sys
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE/'tools'))
spec=importlib.util.spec_from_file_location('editor_cache_server',HERE.parents[1]/'scripts/play_web.py');server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
with tempfile.TemporaryDirectory(prefix='dojo-editor-cache-') as temp:
    root=Path(temp);game=root/'game';server.GAME=game;server.ROOT=root
    names=['src/main.lua','src/art.lua','src/cpu.lua','assets/techniques.json','assets/import.json','browser/template.html','browser/fengari-web.js','browser/runtime-provenance.json','tools/build.py','assets/characters.json','assets/character-assets.json','assets/specials.json','assets/special-assets.json','assets/character-visuals.json','tools/skin_palette.py']
    for name in names:p=game/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('input')
    (game/'src/assets').mkdir();calls=[];saved=server.subprocess.run
    def build(*args,**kwargs):
        calls.append(1);(game/'assets/character-visuals.json').write_text('derived '+str(len(calls)))
        (game/'dist').mkdir(exist_ok=True);(game/'dist'/server.PAGE).write_text('finished game')
    server.subprocess.run=build
    try:
        builder=server.Builder();builder.refresh();builder.refresh();assert len(calls)==1,'Own outputs caused another build'
        (game/'tools/skin_palette.py').write_text('new palette revision');builder.refresh();builder.refresh();assert len(calls)==2,'Palette edit not detected or repeated'
    finally:server.subprocess.run=saved
print('PASS one build per source revision; derived visual metadata does not loop rebuilds')
