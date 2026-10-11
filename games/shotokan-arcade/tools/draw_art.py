"""Original pixel art, indexed palette, deduplicated legacy TIC-80 tile sheets.
All poses and pixels are authored here. No imported franchise imagery.
"""
from pathlib import Path
import json,math
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
PALETTE=['11141f','202531','4a5360','332a35','654838','9c6c47','cc9b62','f4d8a0','faf4e7','c5cdc8','889a9a','4f7683','dc594c','509cad','9ba567','4b6256']
PROFILES=json.loads((ROOT/'src/characters.json').read_text())
RGB=[tuple(bytes.fromhex(c)) for c in PALETTE]
def picture(w,h):
 im=Image.new('P',(w,h),0);im.putpalette([v for c in RGB for v in c]+[0]*(768-48));return im

HURT={}
def fighter(kind,pose):
 im=picture(72,64);d=ImageDraw.Draw(im)
 profile=PROFILES[kind];female=profile['hair']=='ponytail';belt=profile['belt'];skin=profile['skin_shadow'];light=profile['skin_highlight'];hair=profile['hair_shadow'];hairlight=profile['hair_highlight']
 # Individual pose design: hip, lean, knee/foot positions and fist positions.
 hip=(29,37);lean=1;bob=profile['height_offset'];twist=0
 rear=[(27,38),(23,49),(17,59)];front=[(32,38),(39,48),(44,60)]
 fararm=[(29,21),(24,29),(34,32)];neararm=[(37,21),(43,27),(47,20)]
 if pose=='idle1':bob+=1;neararm=[(37,22),(43,28),(47,21)]
 elif pose=='step0':rear=[(27,38),(25,49),(24,61)];front=[(32,38),(41,46),(49,59)];lean=2
 elif pose=='step1':rear=[(27,38),(19,49),(13,60)];front=[(32,38),(36,49),(38,61)];lean=-1
 elif pose=='guard':lean=-2;neararm=[(35,21),(40,24),(41,14)];fararm=[(28,21),(33,28),(38,23)]
 elif pose=='react':lean=-5;neararm=[(31,23),(38,29),(44,26)];fararm=[(24,21),(19,28),(14,23)]
 elif pose=='recover':lean=0;neararm=[(35,21),(42,29),(39,34)]
 elif pose=='oi0':lean=-1;neararm=[(36,21),(36,30),(28,34)];fararm=[(28,21),(36,25),(43,23)]
 elif pose=='oi1':lean=4;rear=[(27,38),(20,49),(13,61)];front=[(34,38),(42,47),(48,61)];neararm=[(40,22),(50,26),(61,26)];fararm=[(31,22),(27,30),(32,34)]
 elif pose=='gyaku0':lean=-2;neararm=[(35,21),(40,25),(43,20)];fararm=[(26,22),(23,29),(29,34)]
 elif pose=='gyaku1':lean=3;neararm=[(39,21),(43,29),(32,34)];fararm=[(31,22),(45,27),(59,28)]
 elif pose=='mae0':lean=-1;front=[(32,38),(43,39),(38,50)];rear=[(27,38),(26,49),(25,61)]
 elif pose=='mae1':lean=-3;front=[(32,38),(46,42),(67,40)];rear=[(27,38),(25,49),(24,61)];neararm=[(33,21),(39,26),(44,22)]
 elif pose=='mawashi0':lean=-3;front=[(32,38),(44,34),(39,44)];rear=[(27,38),(25,49),(25,61)];neararm=[(33,21),(40,25),(42,18)]
 elif pose=='mawashi1':lean=-5;front=[(32,37),(45,30),(68,31)];rear=[(27,38),(25,49),(25,61)];neararm=[(31,22),(35,28),(42,23)];fararm=[(23,22),(18,29),(13,24)]
 if pose=='idle2':
  lean=0;neararm=[(36,21),(42,26),(47,21)];fararm=[(28,21),(24,28),(33,31)]
 elif pose=='step2':
  lean=2;rear=[(27,38),(28,49),(29,61)];front=[(32,38),(38,48),(42,61)];neararm=[(37,21),(42,27),(46,22)]
 elif pose=='step3':
  lean=0;rear=[(27,38),(22,48),(19,61)];front=[(32,38),(40,49),(45,61)]
 elif pose=='guard1':
  lean=-3;rear=[(27,38),(21,48),(17,61)];front=[(32,38),(38,49),(43,61)]
  neararm=[(34,21),(39,22),(40,13)];fararm=[(27,21),(33,26),(38,21)]
 elif pose=='block0':
  lean=-4;neararm=[(33,21),(41,23),(42,14)];fararm=[(26,21),(35,27),(41,22)]
 elif pose=='block1':
  lean=-2;neararm=[(35,21),(41,24),(41,16)];fararm=[(28,21),(34,29),(40,24)]
 elif pose=='react1':
  lean=-3;neararm=[(33,22),(40,30),(40,26)];fararm=[(26,22),(21,28),(18,25)]
 elif pose=='oiM':
  lean=2;neararm=[(38,22),(46,25),(53,25)];fararm=[(30,22),(26,30),(32,34)]
  rear=[(27,38),(22,49),(16,61)];front=[(34,38),(41,48),(46,61)]
 elif pose=='oiR':
  lean=2;neararm=[(38,22),(44,28),(46,28)];fararm=[(30,22),(27,30),(33,33)]
 elif pose=='gyakuM':
  lean=1;twist=1;neararm=[(37,21),(41,29),(33,34)];fararm=[(29,22),(39,25),(47,27)]
 elif pose=='gyakuR':
  lean=1;neararm=[(37,21),(42,26),(44,22)];fararm=[(29,22),(35,29),(40,28)]
 elif pose=='maeM':
  lean=-2;front=[(32,38),(47,36),(49,45)];rear=[(27,38),(26,49),(25,61)]
 elif pose=='maeR':
  lean=-2;front=[(32,38),(44,37),(39,50)];rear=[(27,38),(26,49),(25,61)]
 elif pose=='mawashiM':
  lean=-4;twist=1;front=[(32,38),(45,28),(53,33)];rear=[(27,38),(25,49),(25,61)]
  neararm=[(32,22),(38,27),(43,23)];fararm=[(25,22),(20,29),(16,27)]
 elif pose=='mawashiR':
  lean=-3;front=[(32,38),(44,33),(45,45)];rear=[(27,38),(25,49),(25,61)]
  neararm=[(33,22),(39,27),(44,23)]
 elif pose=='victory0':
  lean=0;rear=[(27,38),(25,49),(23,61)];front=[(32,38),(37,49),(39,61)]
  neararm=[(36,21),(43,12),(43,5)];fararm=[(28,21),(25,30),(29,35)]
 elif pose=='victory1':
  lean=0;rear=[(27,38),(25,49),(23,61)];front=[(32,38),(37,49),(39,61)]
  neararm=[(36,21),(43,11),(44,4)];fararm=[(28,21),(25,30),(29,35)]
 elif pose=='defeat':
  lean=-1;bob+=3;neararm=[(35,24),(40,34),(39,40)];fararm=[(27,24),(22,33),(24,39)]
 if pose in ('gyaku0','gyakuM','gyaku1','mawashiM','mawashi1'):twist=1
 # Filled, contoured limb silhouettes: cuff cuts, folds, shadow and highlights.
 def poly(points,fill,outline=1):d.polygon(points,fill=fill);d.line(points+[points[0]],fill=outline,width=1)
 def segment(a,b,wa,wb,fill=9):
  dx,dy=b[0]-a[0],b[1]-a[1];norm=max(math.hypot(dx,dy),1);nx,ny=-dy/norm,dx/norm
  wa*=profile['body_width'];wb*=profile['body_width']
  pts=[(round(a[0]+nx*wa),round(a[1]+ny*wa)),(round(b[0]+nx*wb),round(b[1]+ny*wb)),(round(b[0]-nx*wb),round(b[1]-ny*wb)),(round(a[0]-nx*wa),round(a[1]-ny*wa))]
  poly(pts,fill)
  d.line([(round(a[0]+nx*(wa-1)),round(a[1]+ny*(wa-1))),(round(b[0]+nx*(wb-1)),round(b[1]+ny*(wb-1)))],fill=8,width=2)
  d.line([(round(a[0]-nx*(wa-1)),round(a[1]-ny*(wa-1))),(round(b[0]-nx*(wb-1)),round(b[1]-ny*(wb-1)))],fill=10,width=1)
 def leg(nodes,far=False):
  a,k,f=nodes
  segment(a,k,4,3,10 if far else 9);segment(k,(f[0],f[1]-3),3,2,9 if far else 8)
  # Bare feet, toes and cuff line.
  poly([(f[0]-2,f[1]-3),(f[0]+1,f[1]-3),(f[0]+4,f[1]),(f[0]+4,f[1]+1),(f[0]-3,f[1]+1),(f[0]-3,f[1]-1)],skin)
  d.line([(f[0]-1,f[1]-1),(f[0]+2,f[1])],fill=light)
  d.line([(k[0]-2,k[1]),(k[0]+1,k[1]+2)],fill=10)
 def arm(nodes,far=False):
  a,e,f=nodes
  segment(a,e,3,2,9 if far else 8);segment(e,(f[0]-1,f[1]),2,2,8)
  poly([(f[0]-2,f[1]-2),(f[0]+1,f[1]-3),(f[0]+3,f[1]-1),(f[0]+3,f[1]+2),(f[0]-1,f[1]+2),(f[0]-2,f[1]+1)],skin)
  d.line([(f[0],f[1]-1),(f[0]+2,f[1]-1)],fill=light)
  d.point((f[0]+1,f[1]+1),fill=5)
 # Rear limb is occluded by torso; forward knee/foot remains distinct.
 leg(rear,True);leg(front);arm(fararm,True)
 cx=32+lean;cy=21+bob
 half=(6 if female else 8)-twist
 torso=[(cx-half+1,cy-2),(cx+half-2,cy-2),(cx+half,cy+3),(cx+5,cy+9),(cx+4,37),(cx+6,42),(cx-9,42),(cx-8,37),(cx-7,cy+6)]
 poly(torso,9)
 d.line([(cx-half+2,cy),(cx-half+1,cy+5)],fill=8)
 poly([(cx-4,cy),(cx,cy+2),(cx+2,35),(cx-5,37),(cx-6,cy+5)],8,9)
 d.polygon([(cx+4,cy+3),(cx+6,cy+6),(cx+3,36),(cx,36),(cx+1,28)],fill=10)
 # Jacket overlap, V-shaped lapel, folds, stitch lines.
 poly([(cx-3,cy-3),(cx+2,cy-3),(cx+3,cy+1),(cx-1,cy+6)],skin)
 d.line([(cx-4,cy-2),(cx,cy+7),(cx+3,cy+1)],fill=1)
 d.line([(cx-5,cy-1),(cx-1,cy+8),(cx-4,35)],fill=8,width=1)
 d.line([(cx+4-twist*3,30),(cx+1-twist*2,34)],fill=8)
 d.line([(cx+3,32),(cx+4,34)],fill=10)
 d.line([(cx-6,39),(cx-3,40)],fill=10)
 d.point((cx+3,40),fill=8)
 d.line([(cx-5,32),(cx-3,35)],fill=10)
 d.polygon([(cx-8,36),(cx+4,35+twist),(cx+5,38+twist),(cx-7,39)],fill=belt)
 d.line([(cx-7,36),(cx+3,35+twist)],fill=light)
 poly([(cx-2-twist,37),(cx+1-twist,37),(cx+1-twist,43),(cx-1-twist*2,47),(cx-3-twist*2,46)],belt)
 d.line([(cx,39),(cx-1,43)],fill=1)
 # Raised knee passes in front of the lower jacket; standing feet stay grounded.
 if pose.startswith('mae') or pose.startswith('mawashi'):leg(front)
 else:d.line([(front[1][0]-2,front[1][1]-1),(front[1][0],front[1][1]+2)],fill=10)
 arm(neararm)
 # Expressive head silhouette, nose/eye/ear; no rectangular head placeholder.
 hx=cx+1;hy=9+bob
 poly([(hx-4,hy-3),(hx+2,hy-3),(hx+4,hy),(hx+4,hy+2),(hx+6,hy+3),(hx+5,hy+4),(hx+4,hy+4),(hx+3,hy+8),(hx,hy+9),(hx-profile["jaw"],hy+6),(hx-5,hy+2)],skin)
 d.polygon([(hx,hy),(hx+3,hy),(hx+3,hy+3),(hx+4,hy+3),(hx+3,hy+6),(hx+1,hy+7),(hx-1,hy+5)],fill=light)
 d.line([(hx+1,hy),(hx+3,hy+1)],fill=1);d.point((hx+2,hy+2),fill=1);d.point((hx+3,hy+2),fill=8)
 d.line([(hx-1,hy+6),(hx+1,hy+7)],fill=5)
 d.line([(hx+1,hy+6),(hx+3,hy+6)],fill=5)
 d.point((hx-3,hy+2),fill=light);d.point((hx-2,hy+3),fill=5)
 if female:
  poly([(hx-5,hy-2),(hx-3,hy-5),(hx+1,hy-5),(hx+3,hy-2),(hx+2,hy),(hx-1,hy-1),(hx-3,hy+1),(hx-4,hy+4),(hx-5,hy+3)],hair)
  poly([(hx-6,hy-1),(hx-8,hy-2),(hx-10,hy),(hx-9,hy+4),(hx-7,hy+8),(hx-6,hy+9),(hx-7,hy+3)],hair)
  d.line([(hx-3,hy-4),(hx,hy-4)],fill=hairlight)
  d.point((hx-6,hy),fill=belt)
 else:
  poly([(hx-5,hy-2),(hx-4,hy-4),(hx-1,hy-5),(hx+2,hy-4),(hx+4,hy-2),(hx+2,hy),(hx,hy-1),(hx-2,hy+1),(hx-3,hy+2),(hx-4,hy+4),(hx-5,hy+2)],hair)
  d.line([(hx-3,hy-3),(hx,hy-3)],fill=hairlight);d.point((hx+1,hy-2),fill=hairlight)
 HURT.setdefault(kind,{})[pose]={'x':cx-32-(6 if female else 7),'y':cy,'w':12 if female else 14,'h':25}
 return im

POSES=['idle0','idle1','idle2','step0','step1','step2','step3','guard','guard1','block0','block1','react','react1','recover','oi0','oiM','oi1','oiR','gyaku0','gyakuM','gyaku1','gyakuR','mae0','maeM','mae1','maeR','mawashi0','mawashiM','mawashi1','mawashiR','victory0','victory1','defeat']
def dojo():
 im=picture(240,136);d=ImageDraw.Draw(im)
 d.rectangle((0,0,239,135),fill=3)
 # Warm timber, recessed shoji, depth via foreground beams and floor perspective.
 d.rectangle((8,25,231,91),fill=4)
 for y in range(27,89,8):
  d.line((9,y,230,y),fill=5);d.line((9,y+7,230,y+7),fill=3)
  for x in range(15+(y%3)*7,224,38):d.line((x,y+4,x+14,y+4),fill=4)
 for xa in [22,160]:
  d.rectangle((xa-3,32,xa+60,73),fill=3);d.rectangle((xa,35,xa+57,68),fill=11)
  d.rectangle((xa+1,36,xa+56,49),fill=10)
  for x in range(xa+2,xa+56,11):d.line((x,35,x,68),fill=4)
  for y in range(36,69,8):d.line((xa,y,xa+57,y),fill=4)
  d.line((xa,70,xa+57,70),fill=6)
  d.rectangle((xa-4,74,xa+61,76),fill=5)
 # Upper transom and joinery, subtle wall grain, central dojo crest.
 for x in range(25,218,12):
  d.line((x,29,x+5,31),fill=4)
 for x in [91,149]:
  d.rectangle((x-5,73,x+5,75),fill=5)
  d.polygon([(x-3,72),(x+3,72),(x+2,77),(x-2,77)],fill=3)
  d.line((x,71,x-1,65),fill=6)
  d.line((x-1,67,x+3,65),fill=4)
  d.ellipse((x-6,61,x+1,65),fill=15)
  d.ellipse((x-2,59,x+4,63),fill=15)
  d.line((x-4,62,x,62),fill=14)
 # Kamiza platform and original calligraphy scroll.
 d.rectangle((96,81,146,89),fill=3);d.line((95,81,147,81),fill=5)
 for x in range(99,145,7):d.line((x,83,x,88),fill=4)
 d.rectangle((104,30,138,34),fill=3);d.rectangle((108,33,134,76),fill=6)
 d.rectangle((112,35,130,73),fill=7)
 d.line((110,32,132,32),fill=5);d.line((108,76,134,76),fill=3)
 # Hand-drawn kanji-inspired brush strokes: karate-do tribute, no copied logo.
 for dx,dy,ex,ey in [(116,39,125,39),(120,37,120,44),(115,43,126,43),(117,46,124,46),(120,44,120,50),(115,49,125,49),(115,54,125,54),(119,52,119,59),(115,57,124,57),(122,57,122,61),(116,63,124,63),(115,65,115,69),(115,69,126,69),(120,61,120,68)]:d.line((dx,dy,ex,ey),fill=3,width=1)
 for x in [8,228]:
  d.rectangle((x-3,24,x+4,93),fill=3);d.line((x-2,25,x-2,90),fill=6);d.line((x+1,26,x+1,91),fill=4)
 d.rectangle((0,25,239,28),fill=3);d.line((0,27,239,27),fill=5)
 # Lanterns and subtle reflected warm light.
 for x in [10,230]:
  d.line((x,28,x,36),fill=1)
  d.ellipse((x-5,36,x+5,49),fill=6,outline=3)
  d.line((x-3,40,x+3,40),fill=7);d.line((x-3,44,x+3,44),fill=7)
  d.line((x,37,x,47),fill=5)
 d.rectangle((0,90,239,94),fill=3);d.line((0,93,239,93),fill=5)
 d.line((0,95,239,95),fill=3)
 # Tatami strips perspective, a central competition boundary and woven texture.
 d.rectangle((0,95,239,135),fill=15)
 for y in range(96,136,2):
  for x in range(y%4,240,6):d.point((x,y),fill=14 if (x+y)%17==0 else 15)
 for y in [99,106,118,134]:d.line((0,y,239,y),fill=11)
 for x in [-140,-55,35,120,205,295,380]:d.line((120+(x-120)*.2,95,x,135),fill=11)
 d.line((41,102,200,102),fill=14);d.line((41,102,20,129),fill=14);d.line((200,102,220,129),fill=14);d.line((20,129,220,129),fill=14)
 return im

# Transparent tiles omitted, identical 8x8 tiles reused across both characters.
frames={};tiles=[];indices={}
for who in ['ren','aki']:
 frames[who]={}
 sheet=picture(72*len(POSES),64)
 for idx,pose in enumerate(POSES):
  im=fighter(who,pose);im.save(ROOT/'assets'/f'{who}-{pose}.png');sheet.paste(im,(idx*72,0))
  cells=[]
  for y in range(0,64,8):
   for x in range(0,72,8):
    pix=im.crop((x,y,x+8,y+8)).tobytes()
    if not any(pix):continue
    if pix not in indices:indices[pix]=len(tiles);tiles.append(pix)
    cells.append([x,y,indices[pix]])
  frames[who][pose]=cells
 sheet.save(ROOT/'assets'/f'{who}-sheet.png')
if len(tiles)>990:raise SystemExit(f'Asset budget exceeded: {len(tiles)}/990 logical tiles (480 resident + 510 map cache)')
def packed(pixels):return bytes(pixels[i]|pixels[i+1]<<4 for i in range(0,len(pixels),2))
(ROOT/'assets/tiles.bin').write_bytes(b''.join(packed(p) for p in tiles))
bg=dojo();bg.save(ROOT/'assets/dojo.png');(ROOT/'assets/dojo.bin').write_bytes(packed(bg.tobytes()))
(ROOT/'assets/palette.bin').write_bytes(b''.join(bytes.fromhex(c) for c in PALETTE))
(ROOT/'assets/atlas.json').write_text(json.dumps({'palette':PALETTE,'frames':frames,'tiles':len(tiles),'poses':POSES,'hurt':HURT},separators=(',',':'))+'\n')
lua='ART={\n'
for who,poses in frames.items():
 lua+=who+'={\n'
 for pose,cells in poses.items():lua+=pose+'={'+','.join('{'+','.join(map(str,c))+'}' for c in cells)+'},\n'
 lua+='},\n'
lua+='}\nHURT={\n'
for who,poses in HURT.items():
 lua+=who+'={\n'
 for pose,b in poses.items():lua+=pose+'={'+','.join(k+'='+str(v) for k,v in b.items())+'},\n'
 lua+='},\n'
lua+='}\n'
(ROOT/'src/art.lua').write_text(lua)
print('Original art:',len(tiles),'/990 packed tiles;',len(POSES),'poses per character')
