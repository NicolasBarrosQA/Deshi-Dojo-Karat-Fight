"""Reproduce only the historical desktop investigation; does not install on Pi."""
from pathlib import Path
import hashlib,io,json,subprocess,tarfile,urllib.request
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
lock=json.loads((HERE/'provenance.json').read_text());cache=ROOT/'.cache/lutro-research';source=cache/'source'
archive=cache/'source.tar.gz'
cache.mkdir(exist_ok=True)
if not archive.exists():
 with urllib.request.urlopen(lock['source_url'],timeout=60) as response:payload=response.read()
 if hashlib.sha256(payload).hexdigest()!=lock['archive_sha256']:raise SystemExit('Historical archive rejected: SHA-256 mismatch')
 archive.write_bytes(payload)
payload=archive.read_bytes()
assert hashlib.sha256(payload).hexdigest()==lock['archive_sha256']
if not (source/'Makefile').exists():
 with tarfile.open(fileobj=io.BytesIO(payload),mode='r:gz') as tar:
  for member in tar.getmembers():
   if not member.isfile():continue
   parts=Path(member.name).parts[1:]
   assert parts and not any(part in ('.','..') for part in parts)
   target=source/Path(*parts);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(tar.extractfile(member).read())
# Preserve source; -fcommon restores the compiler behavior contemporary to 2019.
if not (source/'lutro_libretro.so').exists():
 import os
 environment=os.environ.copy();environment['CFLAGS']='-fcommon'
 subprocess.run(['make','-j4','platform=unix','WANT_JIT=0'],cwd=source,env=environment,check=True)
print('Historical source archive verified; x86-64 Lutro research runtime prepared')
