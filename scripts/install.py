"""Install a checksum-pinned official release without changing game sources."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'engine/engine.json').read_text())


def install():
    system = platform.system().lower()
    if system not in CONFIG['platforms'] or platform.machine().lower() not in ('x86_64', 'amd64'):
        raise SystemExit('Esta instalação suporta Linux/Windows x86-64.')
    spec = CONFIG['platforms'][system]
    runtime = ROOT / '.runtime' / CONFIG['version'] / system
    cache = ROOT / '.cache'
    cache.mkdir(exist_ok=True)
    archive = cache / spec['asset']
    if not archive.exists():
        url = CONFIG['release_url'].replace('/tag/', '/download/') + '/' + spec['asset']
        with tempfile.NamedTemporaryFile(dir=cache, delete=False) as download:
            temporary = Path(download.name)
            try:
                with urllib.request.urlopen(url, timeout=120) as response:
                    shutil.copyfileobj(response, download)
            except BaseException:
                temporary.unlink(missing_ok=True)
                raise
        temporary.replace(archive)
    with archive.open('rb') as downloaded:
        digest = hashlib.file_digest(downloaded, 'sha256').hexdigest()
    if digest != spec['sha256']:
        raise SystemExit(f'Checksum inválido: {archive}. Remova o arquivo e repita a instalação.')
    marker = runtime / '.installed-sha256'
    if marker.exists():
        if marker.read_text().strip() != digest or not (runtime / spec['binary']).exists():
            raise SystemExit('Instalação inconsistente; preserve seus arquivos antes de remover .runtime.')
        print(f'Instalação já verificada: {runtime}')
        return runtime, spec
    if runtime.exists():
        raise SystemExit(f'Diretório incompleto existente: {runtime}; preserve-o antes de reinstalar.')
    runtime.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=runtime.parent) as staging:
        staging = Path(staging)
        with zipfile.ZipFile(archive) as package:
            for item in package.infolist():
                target = (staging / item.filename).resolve()
                if not target.is_relative_to(staging.resolve()):
                    raise SystemExit('Caminho inseguro no ZIP.')
            package.extractall(staging)
        binary = staging / spec['binary']
        if not binary.is_file() or not (staging / 'external/script/main.lua').is_file():
            raise SystemExit('Pacote oficial sem os arquivos esperados.')
        if os.name != 'nt':
            binary.chmod(0o755)
        (staging / '.installed-sha256').write_text(digest + '\n')
        staging.rename(runtime)
    print(f'IKEMEN GO {CONFIG["version"]} instalado: {runtime}')
    return runtime, spec


if __name__ == '__main__':
    install()
