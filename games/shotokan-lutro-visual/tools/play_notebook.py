"""Play the historical desktop core locally. Browser HTML needs no Python."""
import argparse,time,tkinter as tk
from pathlib import Path
from PIL import Image,ImageTk
from native_host import Native
HERE=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--frames',type=int,default=0);args=parser.parse_args()
window=tk.Tk();window.title('Deshi Dojo — prova visual Shotokan')
label=tk.Label(window,bg='#111b20');label.pack()
tk.Label(window,text='P1: setas / Z soco / X defesa / A chute     P2: I J K L / F soco / G defesa / H chute     Enter: recomeçar     F2: CPU/nível/2 jogadores',bg='#111b20',fg='#eadbc1').pack(fill='x')
keymap={'Up':(0,4),'Down':(0,5),'a':(0,8),'i':(1,4),'k':(1,5),'h':(1,8),'Left':(0,6),'Right':(0,7),'z':(0,0),'x':(0,1),'j':(1,6),'l':(1,7),'f':(1,0),'g':(1,1),'Return':(0,3),'F2':(0,2)}
held=set();count=0;core=Native(HERE/'dist/deshi-dojo-visual.lutro')
def press(event):
 if event.keysym in keymap:held.add(keymap[event.keysym])
def release(event):
 if event.keysym in keymap:held.discard(keymap[event.keysym])
def close():
 core.close();window.destroy()
window.bind('<KeyPress>',press);window.bind('<KeyRelease>',release);window.bind('<FocusOut>',lambda event:held.clear())
window.protocol('WM_DELETE_WINDOW',close)
deadline=time.monotonic()
def update():
 global count,deadline
 core.step(1,held);count+=1
 im=ImageTk.PhotoImage(core.frame.resize((1152,672),Image.Resampling.NEAREST));label.configure(image=im);label.image=im
 if args.frames and count>=args.frames:print('PASS historical desktop viewer:',count,'frames');close();return
 deadline+=1/60
 window.after(max(1,round((deadline-time.monotonic())*1000)),update)
window.after(0,update);window.mainloop()
