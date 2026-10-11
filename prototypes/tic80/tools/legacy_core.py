"""Minimal offline libretro host used by the notebook viewer (no saves/network)."""
import ctypes as C
import struct
import zlib

ENV = C.CFUNCTYPE(C.c_bool, C.c_uint, C.c_void_p)
VIDEO = C.CFUNCTYPE(None, C.c_void_p, C.c_uint, C.c_uint, C.c_size_t)
AUDIO = C.CFUNCTYPE(None, C.c_int16, C.c_int16)
BATCH = C.CFUNCTYPE(C.c_size_t, C.c_void_p, C.c_size_t)
POLL = C.CFUNCTYPE(None)
INPUT = C.CFUNCTYPE(C.c_int16, C.c_uint, C.c_uint, C.c_uint, C.c_uint)
LOG = C.CFUNCTYPE(None, C.c_int, C.c_char_p)
MAPPING = [4,5,6,7,0,8,1,9]
class Game(C.Structure):
    _fields_=[('path',C.c_char_p),('data',C.c_void_p),('size',C.c_size_t),('meta',C.c_char_p)]

class Core:
    def __init__(self,path,cart):
        self.buttons=set()
        self.errors=[]
        self.frame=None
        self.core=C.CDLL(str(path))
        self.callbacks=[]
        def log(level,text):
            if level>=3:
                self.errors.append(text.decode(errors='replace'))
        self.logger=LOG(log)
        def env(command,data):
            if command==27:
                C.cast(data,C.POINTER(C.c_void_p))[0]=C.cast(self.logger,C.c_void_p).value
                return True
            if command==10:
                return C.cast(data,C.POINTER(C.c_int))[0]==1
            return False
        def video(data,w,h,pitch):
            if data:
                raw=C.string_at(data,pitch*h)
                rgb=bytearray()
                for y in range(h):
                    row=raw[y*pitch:y*pitch+w*4]
                    for x in range(w):
                        b,g,r,_=row[x*4:x*4+4]
                        rgb.extend((r,g,b))
                self.frame=(w,h,bytes(rgb))
        for name,kind,fn in [('environment',ENV,env),('video_refresh',VIDEO,video),
                ('audio_sample',AUDIO,lambda l,r:None),
                ('audio_sample_batch',BATCH,lambda data,n:n),
                ('input_poll',POLL,lambda:None),
                ('input_state',INPUT,lambda port,device,index,key:int(device==1 and (port,key) in self.buttons))]:
            callback=kind(fn)
            self.callbacks.append(callback)
            function=getattr(self.core,'retro_set_'+name)
            function.argtypes=[kind]
            function(callback)
        self.core.retro_load_game.argtypes=[C.POINTER(Game)]
        self.core.retro_load_game.restype=C.c_bool
        self.core.retro_init()
        self.cart=C.create_string_buffer(cart)
        if not self.core.retro_load_game(C.byref(Game(b'deshi-dojo.tic',C.cast(self.cart,C.c_void_p),len(cart),None))):
            self.close()
            raise RuntimeError('O núcleo rejeitou o cartucho.')
    def key(self,id,down):
        key=(id//8,MAPPING[id%8])
        if down:self.buttons.add(key)
        else:self.buttons.discard(key)
    def tick(self):
        self.core.retro_run()
        if self.errors:raise RuntimeError('\n'.join(self.errors))
    def png(self):
        w,h,rgb=self.frame
        def chunk(kind,data):
            return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
        rows=b''.join(b'\0'+rgb[y*w*3:(y+1)*w*3] for y in range(h))
        return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b'')
    def close(self):
        self.core.retro_unload_game()
        self.core.retro_deinit()
