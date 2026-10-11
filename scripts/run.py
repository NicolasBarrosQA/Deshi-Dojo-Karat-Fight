"""Overlay project content onto the runtime and launch from its working directory."""
import argparse
import os
import re
from pathlib import Path
import shutil
import subprocess
import time
from install import ROOT, install

parser = argparse.ArgumentParser()
parser.add_argument('--demo', action='store_true', help='Luta automática KFM versus KFM')
parser.add_argument('--smoke', action='store_true', help='Luta curta; exige resultado de combate')
args, extra = parser.parse_known_args()
runtime, spec = install()
for source in (ROOT / 'game').rglob('*'):
    if source.is_file() and source.name != 'README.md':
        dest = runtime / source.relative_to(ROOT / 'game')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
shader_cache = ROOT / ".cache" / "mesa"
shader_cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MESA_SHADER_CACHE_DIR", str(shader_cache))
command = [str(runtime / spec['binary'])]
if args.demo or args.smoke:
    command += ['-p1', 'kfm', '-p2', 'kfm', '-p1.ai', '8', '-p2.ai', '8', '-s', 'stages/stage0.def']
if args.smoke:
    results = ROOT / '.cache' / 'smoke'
    results.mkdir(parents=True, exist_ok=True)
    report = results / f'match-{time.time_ns()}.txt'
    command += ['-rounds', '1', '-time', '10', '-log', str(report)]
    command += extra
    completed = subprocess.run(command, cwd=runtime, timeout=90)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    if not report.exists():
        raise SystemExit('O motor terminou sem registrar a luta.')
    text = report.read_text()
    if not (re.search(r'\["LastRound"\] => [1-9][0-9]*', text)
            and re.search(r'\["Timer"\] => [1-9][0-9]*', text)
            and text.count('["Name"] => "Kung Fu Man"') >= 2
            and '["Win"] => true' in text):
        raise SystemExit(f'Resultado de combate incompleto: {report}')
    print(f'Luta concluída e resultado verificado: {report}')
else:
    raise SystemExit(subprocess.call(command + extra, cwd=runtime))
