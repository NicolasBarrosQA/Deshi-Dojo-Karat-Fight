"""Stdlib-only regression for the player's refresh/git-pull workflow."""
from pathlib import Path
import importlib.util,json,sys,tempfile
from windows_checkout import fixture,HERE
spec=importlib.util.spec_from_file_location('dojo_server',HERE.parents[1]/'scripts/play_web.py')
server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
with tempfile.TemporaryDirectory() as tmp:
    game=fixture(tmp);server.GAME=game
    builder=server.Builder();builder.refresh()
    page=game/'dist/deshi-dojo-visual.html';stamp=page.stat().st_mtime_ns
    builder.refresh();assert page.stat().st_mtime_ns==stamp,'unchanged refresh rebuilt the page'
    path=game/'assets/characters.json';data=json.loads(path.read_text())
    data['students']['demo-adult']['name']='ALUNO EXEMPLO';path.write_text(json.dumps(data))
    builder.refresh();assert 'ALUNO EXEMPLO' in page.read_text(encoding='utf-8')
    stamp=page.stat().st_mtime_ns;builder.refresh();assert page.stat().st_mtime_ns==stamp
    assert not list((game/'dist').glob('*.zip'))
print('PASS character roster changes rebuild offline HTML; unchanged refresh is stable; no ZIPs or external dependencies')
