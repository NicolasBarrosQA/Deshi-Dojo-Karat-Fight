"""Regression: Windows-style Git line endings must not disable integrity checks.

Runs with Python only in isolated game fixtures, not on user/runtime files.
No native Windows machine is required to reproduce the byte conversion.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parents[1]


def fixture(parent):
    game = Path(parent) / 'game'
    for name in ('browser', 'src', 'tools'):
        shutil.copytree(HERE / name, game / name,
                        ignore=shutil.ignore_patterns('__pycache__', 'pose-*.png'))
    (game / 'assets').mkdir()
    for name in ('techniques.json', 'specials.json', 'ceremony.json', 'import.json', 'characters.json', 'character-assets.json'):
        shutil.copyfile(HERE / 'assets' / name, game / 'assets' / name)
    if (HERE/'assets/character-visuals.json').exists():shutil.copyfile(HERE/'assets/character-visuals.json',game/'assets/character-visuals.json')
    for name in ('special-assets.json','special-profiles.json','ceremony-assets.json','hand-touch-assets.json'):
        if (HERE/'assets'/name).exists():shutil.copyfile(HERE/'assets'/name,game/'assets'/name)
    for name in ('character-identities.json','identity-adult-attachments.json','character-masks.json'):
        if (HERE/'assets'/name).exists():shutil.copyfile(HERE/'assets'/name,game/'assets'/name)
    source=HERE/'assets/source/identities'
    if source.exists():shutil.copytree(source,game/'assets/source/identities')
    return game


def build(game, optimized=False):
    return subprocess.run([sys.executable] + (['-O'] if optimized else []) +
                          [str(game / 'tools/build.py'), '--web-only'],
                          capture_output=True, text=True, timeout=30)


def main():
    with tempfile.TemporaryDirectory(prefix='shotokan-checkout-') as tmp:
        game = fixture(tmp)
        runtime = game / 'browser/fengari-web.js'
        original = runtime.read_bytes()
        pin = json.loads((game / 'browser/runtime-provenance.json').read_text(
            encoding='utf-8'))['runtime_sha256']
        assert hashlib.sha256(original).hexdigest() == pin
        result = build(game)
        assert result.returncode == 0, result.stderr
        expected_page = (game / 'dist/deshi-dojo-visual.html').read_bytes()
        # Emulate core.autocrlf=true on all inputs read as text, not just the VM.
        for path in game.rglob('*'):
            if path.is_file() and path.suffix in ('.js', '.lua', '.json', '.html', '.py'):
                raw = path.read_bytes().replace(b'\r\n', b'\n')
                path.write_bytes(raw.replace(b'\n', b'\r\n'))
        result = build(game)
        assert result.returncode == 0, result.stderr
        assert runtime.read_bytes() == original
        assert (game / 'dist/deshi-dojo-visual.html').read_bytes() == expected_page
        print('PASS LF and Windows CRLF inputs build the same page; pinned runtime restored')
        # Successful repeat must not rewrite the interpreter again.
        stamp = runtime.stat().st_mtime_ns
        assert build(game).returncode == 0
        assert runtime.stat().st_mtime_ns == stamp
        print('PASS repeat build preserves the verified runtime')
        # A real content change must fail even when Python assertions are disabled.
        for crlf in (False, True):
            damaged = original + b'\n/* unexpected content */\n'
            if crlf:
                damaged = damaged.replace(b'\n', b'\r\n')
            runtime.write_bytes(damaged)
            result = build(game, optimized=True)
            assert result.returncode != 0 and 'Fengari' in result.stderr
            assert runtime.read_bytes() == damaged
        print('PASS modified LF/CRLF interpreters rejected under python -O without overwriting them')


if __name__ == '__main__':
    main()
