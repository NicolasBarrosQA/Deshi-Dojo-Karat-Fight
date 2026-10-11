"""Run cartridge integrity, Lua logic and historical libretro checks offline."""
from pathlib import Path
import hashlib
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parents[1]
cart=(HERE/'dist/deshi-dojo.tic').read_bytes()
source=(HERE/'src/dojo.lua').read_bytes()
chunks={}
position=0
while position<len(cart):
    assert position+4<=len(cart),'Cabeçalho truncado'
    header,size,reserved=struct.unpack_from('<BHB',cart,position)
    position+=4
    assert reserved==0 and header>>5==0,'Formato fora do banco legado 0'
    assert position+size<=len(cart),'Payload truncado'
    assert header not in chunks,'Chunk duplicado'
    chunks[header]=cart[position:position+size]
    position+=size
assert chunks[5]==source,'Cartucho desatualizado em relação ao Lua'
assert set(chunks)=={5,12} and len(chunks[12])==48
checksum=(HERE/'dist/SHA256SUMS.txt').read_text().split()[0]
assert hashlib.sha256(cart).hexdigest()==checksum
print('PASS integridade: Lua idêntico, chunks legados e checksum',flush=True)
subprocess.run([str(ROOT/'.cache/tic80-legacy/lua53'),str(HERE/'tests/combat.lua'),str(HERE/'src/dojo.lua')],check=True)
subprocess.run([sys.executable,str(HERE/'tests/libretro_smoke.py')],check=True)
