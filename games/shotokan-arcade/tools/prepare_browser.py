"""Prepare the pinned MIT Lua browser VM; never needed during gameplay."""
import base64
import hashlib
import io
import json
from pathlib import Path
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
lock = json.loads((HERE / 'browser/runtime-provenance.json').read_text())
dest = ROOT / '.cache/fengari-web'
runtime = dest / 'fengari-web.js'
if runtime.exists() and hashlib.sha256(runtime.read_bytes()).hexdigest() == lock['runtime_sha256']:
    print('Verified cached Fengari ' + lock['version'])
else:
    with urllib.request.urlopen(lock['url'], timeout=60) as response:
        archive = response.read()
    actual = 'sha512-' + base64.b64encode(hashlib.sha512(archive).digest()).decode()
    if actual != lock['integrity']:
        raise SystemExit('Fengari archive integrity mismatch; artifact rejected.')
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as tar:
        javascript = tar.extractfile('package/dist/fengari-web.js').read()
        license_text = tar.extractfile('package/LICENSE').read()
    if hashlib.sha256(javascript).hexdigest() != lock['runtime_sha256']:
        raise SystemExit('Fengari runtime SHA-256 mismatch; artifact rejected.')
    dest.mkdir(parents=True, exist_ok=True)
    runtime.write_bytes(javascript)
    (dest / 'LICENSE').write_bytes(license_text)
    print('Downloaded and verified Fengari ' + lock['version'])
