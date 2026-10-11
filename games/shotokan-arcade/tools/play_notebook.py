"""Offline desktop viewer: Python stdlib, Tk and a prepared native legacy core."""
import argparse
import base64
from pathlib import Path
import time
import tkinter as tk
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/"prototypes/tic80/tools"))
from legacy_core import Core

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--core',type=Path,default=ROOT/'.cache/tic80-legacy/tic80_libretro.so')
parser.add_argument('--frames',type=int,default=0,help='Encerrar após N frames; 0=interativo')
parser.add_argument('--capture',type=Path,help='Salvar último frame em PNG')
args=parser.parse_args()
if not args.core.exists():
    raise SystemExit('Prepare o núcleo com tools/build_runtime.py ou informe --core.')
core=Core(args.core,(HERE/'dist/shotokan-arcade.tic').read_bytes())
root=tk.Tk()
root.title('Deshi Dojo Karate Fight — Shotokan Arcade')
label=tk.Label(root,bg='black')
label.pack()
tk.Label(root,text='P1: setas + Z X A S | P2: I K J L + F G R T\nZ/F confirma seleção. Recuar defende. P1 Z+X por 1s: diagnóstico. Esc fecha.').pack()
keys={'Up':0,'Down':1,'Left':2,'Right':3,'z':4,'x':5,'a':6,'s':7,
      'i':8,'k':9,'j':10,'l':11,'f':12,'g':13,'r':14,'t':15}
root.bind('<KeyPress>',lambda e:core.key(keys[e.keysym],True) if e.keysym in keys else None)
root.bind('<KeyRelease>',lambda e:core.key(keys[e.keysym],False) if e.keysym in keys else None)
root.bind('<FocusOut>',lambda e:core.buttons.clear())
root.bind('<Escape>',lambda e:root.destroy())
root.protocol('WM_DELETE_WINDOW',root.destroy)
frames=0
due=time.monotonic()
error=None

def refresh():
    global frames,due,error
    try:
        core.tick()
        frames+=1
        label.image=tk.PhotoImage(data=base64.b64encode(core.png())).zoom(3,3)
        label.configure(image=label.image)
        if args.frames and frames>=args.frames:
            root.destroy()
            return
        due+=1/60
        if due<time.monotonic()-0.1:due=time.monotonic()
        root.after(max(1,int((due-time.monotonic())*1000)),refresh)
    except Exception as exception:
        error=exception
        root.destroy()
root.after(0,refresh)
try:
    root.mainloop()
finally:
    if args.capture and core.frame:
        args.capture.parent.mkdir(parents=True,exist_ok=True)
        args.capture.write_bytes(core.png())
    core.close()
if error:raise error
print(f'Execução offline encerrada: {frames} frames.')
