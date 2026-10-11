"""Exercise the actual 2019 libretro input/rendering paths without a GUI."""
import ctypes as C
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[3]
PROTOTYPE = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache/tic80-legacy'
OUTPUT = CACHE / 'results'
OUTPUT.mkdir(exist_ok=True)
ENV = C.CFUNCTYPE(C.c_bool, C.c_uint, C.c_void_p)
VIDEO = C.CFUNCTYPE(None, C.c_void_p, C.c_uint, C.c_uint, C.c_size_t)
AUDIO = C.CFUNCTYPE(None, C.c_int16, C.c_int16)
BATCH = C.CFUNCTYPE(C.c_size_t, C.c_void_p, C.c_size_t)
POLL = C.CFUNCTYPE(None)
INPUT = C.CFUNCTYPE(C.c_int16, C.c_uint, C.c_uint, C.c_uint, C.c_uint)
LOG = C.CFUNCTYPE(None, C.c_int, C.c_char_p)
class Game(C.Structure):
    _fields_ = [('path', C.c_char_p), ('data', C.c_void_p), ('size', C.c_size_t), ('meta', C.c_char_p)]
class Info(C.Structure):
    _fields_ = [('name', C.c_char_p), ('version', C.c_char_p), ('extensions', C.c_char_p), ('fullpath', C.c_bool), ('block', C.c_bool)]

# Mapping verified in the historical tic80_libretro_update_gamepad function.
MAPPING = [4, 5, 6, 7, 0, 8, 1, 9]
buttons = set()
errors = []
frames = []
@LOG
def logger(level, text):
    if level >= 3:
        errors.append(text.decode(errors='replace'))
@ENV
def environment(command, data):
    if command == 27:  # GET_LOG_INTERFACE
        C.cast(data, C.POINTER(C.c_void_p))[0] = C.cast(logger, C.c_void_p).value
        return True
    if command == 10:  # SET_PIXEL_FORMAT (XRGB8888)
        return C.cast(data, C.POINTER(C.c_int))[0] == 1
    return False
@VIDEO
def video(data, width, height, pitch):
    if data:
        frames[:] = [(width, height, pitch, C.string_at(data, pitch * height))]
@INPUT
def input_state(port, device, index, button):
    return int(device == 1 and (port, button) in buttons)
@POLL
def poll():
    pass
@AUDIO
def audio(left, right):
    pass
@BATCH
def batch(data, count):
    return count
core = C.CDLL(str(CACHE/'tic80_libretro.so'))
callbacks = [('environment', ENV, environment), ('video_refresh', VIDEO, video),
             ('audio_sample', AUDIO, audio), ('audio_sample_batch', BATCH, batch),
             ('input_poll', POLL, poll), ('input_state', INPUT, input_state)]
for name, kind, callback in callbacks:
    function = getattr(core, 'retro_set_' + name)
    function.argtypes = [kind]
    function(callback)
core.retro_load_game.argtypes = [C.POINTER(Game)]
core.retro_load_game.restype = C.c_bool
core.retro_get_memory_data.argtypes = [C.c_uint]
core.retro_get_memory_data.restype = C.c_void_p
core.retro_get_system_info.argtypes = [C.POINTER(Info)]
info = Info()
core.retro_get_system_info(C.byref(info))
print('Core:', info.name.decode(), info.version.decode())
core.retro_init()
loaded_buffer = None

def load(cart):
    global loaded_buffer
    errors.clear()
    loaded_buffer = C.create_string_buffer(cart)
    assert core.retro_load_game(C.byref(Game(b'deshi-dojo.tic', C.cast(loaded_buffer,C.c_void_p), len(cart), None)))

def step(count, keys=()):
    buttons.clear()
    for key in keys:
        buttons.add((key//8, MAPPING[key%8]))
    for _ in range(count):
        core.retro_run()
    assert not errors, errors

def memory():
    address = core.retro_get_memory_data(0)
    assert address
    return list(C.cast(address, C.POINTER(C.c_uint32))[:10])

def screenshot(name):
    width,height,pitch,raw=frames[0]
    rgb=bytearray()
    for y in range(height):
        rgb.append(0)
        for x in range(width):
            b,g,r,_ = raw[y*pitch+x*4:y*pitch+x*4+4]
            rgb.extend((r,g,b))
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
    image=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(rgb))+chunk(b'IEND',b'')
    (OUTPUT/name).write_bytes(image)

cart=(PROTOTYPE/'dist/deshi-dojo.tic').read_bytes()
load(cart)
step(1)
assert frames and len(set(frames[0][3]))>4
screenshot('diagnostic.png')
step(60,(4,5))
step(1)
screenshot('fight.png')
step(500,(3,10))
step(1,(5,13))
step(6)
print('PASS cartucho entregue: carregamento, ambas as telas, renderizacao e 569 frames sem erro Lua')

# A test-only cartridge appends telemetry through pmem. The delivered cart
# has no telemetry or persistence. Uses the exact same production Lua source.
source=(PROTOTYPE/'src/dojo.lua').read_bytes()+b'''
local original=TIC
function TIC()
 original()
 pmem(0,DD.frame) pmem(1,DD.p[1].x) pmem(2,DD.p[2].x)
 pmem(3,DD.p[1].y) pmem(4,DD.p[2].y)
 pmem(5,DD.p[1].points) pmem(6,DD.p[2].points)
 pmem(7,DD.mode=="fight" and 1 or 0)
 local masks={0,0}
 for i,p in ipairs(DD.p) do
  for b=0,7 do if p.buttons[b] then masks[i]=masks[i]+2^b end end
 end
 pmem(8,masks[1]) pmem(9,masks[2])
end
'''
# Copy the first, palette chunk verbatim and replace only the code chunk.
test_cart=cart[:52]+struct.pack('<BHB',5,len(source),0)+source
load(test_cart)
step(1)
for port in range(2):
    for bit in range(8):
        step(1,(port*8+bit,))
        state=memory()
        assert state[8+port]==2**bit and state[9-port]==0, state
print('PASS 16 entradas: 8 por jogador, sem vazamento entre portas')
step(1)
before=memory()
step(10,(3,8))
after=memory()
assert after[1]==before[1]+10 and after[2]==before[2] and after[4]==before[4]-10
print('PASS movimento independente e simultaneo P1/P2 no core')
step(60,(4,5))
step(1)
assert memory()[7]==1
step(35,(3,10))  # distance 34
step(1,(4,12))  # both oi-zuki advance -> distance 22
step(8)
assert memory()[5:7]==[1,1],memory()
print('PASS colisao e pontuacao simultanea P1/P2 pelo caminho libretro')
step(100)
assert memory()[5:7]==[1,1]
step(60,(6,7))
assert memory()[5:7]==[0,0]
step(1)
step(60,(4,5))
assert memory()[7]==0
print('PASS contato unico, reinicio e retorno ao diagnostico')
core.retro_unload_game()
core.retro_deinit()
print('TOTAL: 6 grupos libretro passaram; imagens em',OUTPUT)
