"""Build a bank-0 2019-compatible cart containing original art and Lua."""
from pathlib import Path
import hashlib,json,struct
ROOT=Path(__file__).resolve().parents[1]
def chunk(kind,data):return struct.pack('<BHB',kind,len(data),0)+data
code=(ROOT/'src/art.lua').read_bytes()+(ROOT/'src/game.lua').read_bytes()
assert 0<len(code)<65536 and b'\0' not in code
sprites=(ROOT/'assets/tiles.bin').read_bytes()
assert len(sprites)%32==0 and len(sprites)<=990*32
resident=sprites[:480*32]
map_data=(ROOT/"assets/dojo.bin").read_bytes()+sprites[480*32:]
assert len(map_data)<=32640
# Tiles and sprites form one contiguous set of 512 4-bpp 8x8 tiles.
cart=chunk(12,(ROOT/'assets/palette.bin').read_bytes())+chunk(1,resident[:8192])+chunk(2,resident[8192:])+chunk(4,map_data)+chunk(9,(ROOT/'assets/sfx.bin').read_bytes())+chunk(10,(ROOT/'assets/waves.bin').read_bytes())+chunk(5,code)
(ROOT/'dist/shotokan-arcade.tic').write_bytes(cart)
(ROOT/'dist/game.lua').write_bytes(code)
(ROOT/'dist/SHA256SUMS.txt').write_text(hashlib.sha256(cart).hexdigest()+'  shotokan-arcade.tic\n')
print('Cart:',len(cart),'bytes; Lua:',len(code),'/65535; art:',len(sprites)//32,'/990 stored tiles; map:',len(map_data),'/32640')
