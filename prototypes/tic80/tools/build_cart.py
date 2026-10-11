"""Generate the uncompressed, bank-0 legacy cartridge format (2019 loader)."""
from pathlib import Path
import hashlib
import struct

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'src/dojo.lua').read_bytes()
if b'\x00' in source or len(source) >= 65536:
    raise SystemExit('Código inválido ou acima do banco legado de 64 KiB.')
# Legacy 4-byte header: low 5 bits chunk kind, high 3 bits bank,
# followed by uint16 payload size (little endian) and reserved byte.
def chunk(kind, payload):
    return struct.pack('<BHB', kind, len(payload), 0) + payload
palette = bytes.fromhex('140c1c44243430346d4e4a4e854c30346524d04648757161597dced27d2c8595a16daa2cd2aa996dc2cadad45edeeed6')
cart = chunk(12, palette) + chunk(5, source)
output = ROOT / 'dist/deshi-dojo.tic'
output.parent.mkdir(exist_ok=True)
output.write_bytes(cart)
(output.parent / 'SHA256SUMS.txt').write_text(hashlib.sha256(cart).hexdigest() + '  deshi-dojo.tic\n')
print(f'{output}: {len(cart)} bytes; Lua {len(source)}/65535 bytes')
