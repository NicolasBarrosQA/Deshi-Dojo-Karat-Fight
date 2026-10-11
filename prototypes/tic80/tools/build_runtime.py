"""Build a local Lua-only historical core; never install on the arcade."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CACHE = ROOT / '.cache/tic80-legacy'
parser = argparse.ArgumentParser()
parser.add_argument('--offline', action='store_true')
args = parser.parse_args()
lock = json.loads((HERE / 'runtime-lock.json').read_text())
CACHE.mkdir(parents=True, exist_ok=True)
for name, spec in lock.items():
    path = CACHE / name
    if not path.exists():
        if args.offline:
            raise SystemExit(f'Dependência local ausente: {name}; prepare antes sem --offline.')
        subprocess.run(['git', 'init', str(path)], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(path), 'remote', 'add', 'origin', spec['url']], check=True)
        subprocess.run(['git', '-C', str(path), 'fetch', '--depth', '1', 'origin', spec['commit']], check=True)
        subprocess.run(['git', '-C', str(path), 'checkout', '--detach', spec['commit']], check=True)
    actual = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != spec['commit']:
        raise SystemExit(f'Revisão inesperada: {name}; não alterada automaticamente.')
    if subprocess.check_output(['git', '-C', str(path), 'status', '--porcelain'], text=True).strip():
        raise SystemExit(f'Dependência modificada: {name}; preserve antes de reconstruir.')
tic, lua, gif, blip = (CACHE / n for n in ('tic80', 'lua', 'giflib', 'blip'))
lua_sources = [p for p in lua.glob('*.c') if p.name not in ('lua.c', 'luac.c', 'ltests.c', 'onelua.c')]
base = ['gcc', '-std=gnu99', '-O2', '-fcommon', '-DLUA_USE_POSIX', '-DLUA_USE_DLOPEN']
includes = ['-I' + str(p) for p in (tic/'include', tic/'src', lua, gif, blip)]
sources = [tic/'src'/n for n in ('tic80.c', 'tic.c', 'tools.c', 'luaapi.c', 'ext/gif.c', 'system/libretro/tic80_libretro.c')]
sources += lua_sources + [gif/n for n in ('dgif_lib.c', 'egif_lib.c', 'gif_err.c', 'gif_font.c', 'gif_hash.c', 'gifalloc.c', 'openbsd-reallocarray.c')]+[blip/'blip_buf.c']
subprocess.run(base + ['-fPIC', '-shared', '-DTIC_BUILD_WITH_LUA', '-DBUILD_PRO'] + includes + [str(p) for p in sources] + ['-lm', '-ldl', '-o', str(CACHE/'tic80_libretro.so')], check=True)
subprocess.run(base + includes + [str(p) for p in lua_sources + [lua/'lua.c']] + ['-lm', '-ldl', '-o', str(CACHE/'lua53')], check=True)
print('Núcleo Lua histórico e interpretador disponíveis em', CACHE)
