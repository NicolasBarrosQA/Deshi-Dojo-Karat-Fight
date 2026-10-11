"""Historical loader/input/API integration; telemetry appended only in memory."""
import ctypes as C
import hashlib
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'prototypes/tic80/tools'))
from legacy_core import Core

cart = (HERE / 'dist/shotokan-arcade.tic').read_bytes()
source = (HERE / 'dist/game.lua').read_bytes()
assert source == (HERE / 'src/art.lua').read_bytes() + (HERE / 'src/game.lua').read_bytes()
assert hashlib.sha256(cart).hexdigest() == (HERE / 'dist/SHA256SUMS.txt').read_text().split()[0]
chunks = []
offset = 0
while offset < len(cart):
    kind, size, bank = struct.unpack_from('<BHB', cart, offset)
    assert bank == 0
    data = cart[offset + 4:offset + 4 + size]
    assert len(data) == size
    chunks.append((kind, data))
    offset += 4 + size
assert offset == len(cart) and dict(chunks)[5] == source
assert [kind for kind, _ in chunks] == [12, 1, 2, 4, 9, 10, 5]
atlas=__import__('json').loads((HERE/'assets/atlas.json').read_text())
assert len(dict(chunks)[1])+len(dict(chunks)[2])==480*32
assert dict(chunks)[4]==(HERE/'assets/dojo.bin').read_bytes()+(HERE/'assets/tiles.bin').read_bytes()[480*32:]
assert len(dict(chunks)[4])<=32640 and atlas['tiles']<=990
assert dict(chunks)[9]==(HERE/'assets/sfx.bin').read_bytes() and len(dict(chunks)[9])==7*66
assert dict(chunks)[10]==(HERE/'assets/waves.bin').read_bytes()
for poses in atlas['frames'].values():
 for cells in poses.values():
  assert all(0<=id<atlas['tiles'] for x,y,id in cells)
print('PASS delivered cartridge: bank-0 chunks, source identity and SHA-256', flush=True)

telemetry = b'''
local original=TIC
function TIC()
 original()
 local modes={title=0,select=1,fight=2,result=3,diagnostic=4}
 pmem(0,modes[G.mode]) pmem(1,math.floor(G.p[1].x*100)) pmem(2,math.floor(G.p[2].x*100))
 pmem(3,G.p[1].score) pmem(4,G.p[2].score) pmem(5,G.clock)
 pmem(6,G.result and G.result.winner or 0)
 for i,c in ipairs(G.inputs) do
  local mask=0 for b=0,7 do if c.held[b] then mask=mask+2^b end end
  pmem(6+i,mask)
 end
end
'''
test_cart = b''.join(struct.pack('<BHB', kind, len(data), 0) + data
                     for kind, data in chunks if kind != 5)
code = source + telemetry
assert len(code) < 65536
test_cart += struct.pack('<BHB', 5, len(code), 0) + code
core = Core(ROOT / '.cache/tic80-legacy/tic80_libretro.so', test_cart)
core.core.retro_get_memory_data.argtypes = [C.c_uint]
core.core.retro_get_memory_data.restype = C.c_void_p

def state():
    address = core.core.retro_get_memory_data(0)
    assert address
    return list(C.cast(address, C.POINTER(C.c_uint32))[:9])

def step(n=1, keys=()):
    core.buttons.clear()
    for key in keys:
        core.key(key, True)
    for _ in range(n):
        core.tick()
    return state()

try:
    assert step()[0] == 0
    assert step(keys=(5,))[0] == 4
    for port in range(2):
        for bit in range(8):
            s = step(keys=(port*8 + bit,))
            assert s[7+port] == 2**bit and s[8-port] == 0, s
    print('PASS diagnostic: 16 independent libretro inputs, eight per port', flush=True)
    step()
    assert step(60, (4,5))[0] == 0
    step()
    assert step(keys=(4,))[0] == 1
    step()
    assert step(keys=(4,12))[0] == 2
    step(36)
    before = state()
    after = step(10, (3,10))
    assert after[1] > before[1] and after[2] < before[2]
    step(40, (3,10))
    step(keys=(5,13))
    assert step(7)[3:5] == [1,1]
    assert step(60)[3:5] == [1,1]
    print('PASS fight: independent movement, simultaneous scoring and one contact per attack', flush=True)
    # P1 scores two mae-geri (1 + 2 + 2 = 5); real time and inputs only.
    for expected in (3,5):
        step(50,(3,10));step(keys=(6,));step(13)
        assert state()[3] == expected
        step(60)
    assert state()[0] == 3 and state()[6] == 1
    assert step(keys=(4,))[0] == 2
    assert state()[3:5] == [0,0] and state()[5] == 3600
    step(36)
    # Timeout with no input; no shortening of the production timer.
    assert step(3600)[0] == 3 and state()[6] == 0
    step(24)
    step(keys=(3,));step()
    assert step(keys=(4,))[0] == 1
    print('PASS match: five-point win, rematch, full 60-second timeout, draw and return to selection', flush=True)
finally:
    core.close()
print('TOTAL: 4 native integration groups passed; telemetry is absent from the delivered .tic')
