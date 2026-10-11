"""Import generated reference art into fixed, foot-aligned game cells.

Mechanical atlas packing/downsampling only: original high-resolution art retained.
No procedural replacement of the authored character or scene.
"""
from pathlib import Path
import hashlib,json,statistics
from array import array
from collections import deque
from PIL import Image,ImageDraw,ImageOps
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[1]
out=HERE/'src/assets';out.mkdir(parents=True,exist_ok=True)
sources=[('karateca-sheet.png',4,3),('defenses.png',3,4),('kicks.png',4,3),('punches.png',4,2)]
# Added sheets keep the existing pose numbers stable.
sources += [('advanced-ground.png',4,4),('airborne.png',4,4),('arcade-refinement.png',4,4)]
def owned_sheet(sheet,rows,cols):
 """Extract each complete connected figure, including cross-cell limbs.

 Ownership is assigned once on the whole sheet, not on already cut cells.
 Disconnected fragments outside the main silhouettes cannot enter the atlas.
 """
 width,height=sheet.size
 alpha=sheet.getchannel('A').point(lambda v:255 if v>=128 else 0).tobytes()
 labels=array('i',[0])*(width*height);components=[]
 for seed,value in enumerate(alpha):
  if not value or labels[seed]:continue
  tag=len(components)+1;labels[seed]=tag;queue=deque([seed]);pixels=[];sx=sy=0
  while queue:
   pos=queue.popleft();pixels.append(pos);sx+=pos%width;sy+=pos//width
   x,y=pos%width,pos//width
   for nxt in (pos-1 if x else -1,pos+1 if x+1<width else -1,
               pos-width if y else -1,pos+width if y+1<height else -1):
    if nxt>=0 and alpha[nxt] and not labels[nxt]:labels[nxt]=tag;queue.append(nxt)
  components.append((pixels,sx/len(pixels),sy/len(pixels)))
 bodies=sorted(components,key=lambda c:len(c[0]),reverse=True)[:rows*cols]
 assert len(bodies)==rows*cols and all(len(c[0])>1000 for c in bodies),'Missing complete figure'
 bodies.sort(key=lambda c:c[2]);ordered=[]
 for row in range(rows):ordered.extend(sorted(bodies[row*cols:(row+1)*cols],key=lambda c:c[1]))
 cells=[]
 for i,(pixels,cx,cy) in enumerate(ordered):
  col,row=i%cols,i//cols
  assert round(col*width/cols)<=cx<round((col+1)*width/cols),(i,'column ownership')
  assert round(row*height/rows)<=cy<round((row+1)*height/rows),(i,'row ownership')
  mask=bytearray(width*height)
  for pos in pixels:mask[pos]=255
  layer=sheet.copy();layer.putalpha(Image.frombytes('L',(width,height),bytes(mask)))
  b=layer.getchannel('A').getbbox()
  left=min(round(col*width/cols),b[0]);right=max(round((col+1)*width/cols),b[2])
  top=min(round(row*height/rows),b[1]);bottom=max(round((row+1)*height/rows),b[3])
  cells.append(layer.crop((left,top,right,bottom)))
 return cells
cells=[];source_reports=[]
for filename,cols,rows in sources:
 source=HERE/'assets/source'/filename
 sheet=Image.open(source).convert('RGBA');group=[]
 owned=owned_sheet(sheet,rows,cols)
 for row in range(rows):
  for col in range(cols):
   cell=owned[row*cols+col] if owned else sheet.crop((round(col*sheet.width/cols),round(row*sheet.height/rows),round((col+1)*sheet.width/cols),round((row+1)*sheet.height/rows)))
   alpha=cell.getchannel('A').point(lambda v:255 if v>=128 else 0)
   cell.putalpha(alpha);bounds=alpha.getbbox();assert bounds,(filename,row,col)
   group.append((cell,bounds))
 scale=128/statistics.median(b[3]-b[1] for _,b in group)
 if filename=='airborne.png':scale=source_reports[-1]['uniform_scale']
 scale=min(scale,140/max(b[3]-b[1] for _,b in group))
 source_reports.append({'file':filename,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'uniform_scale':scale,'poses':len(group)})
 cells.extend((cell,bounds,scale) for cell,bounds in group)
atlas=Image.new('RGBA',(896,144*((len(cells)+3)//4)))
poses=[]
for i,(cell,b,scale) in enumerate(cells):
 # Anchor at the belt, rather than centering the bounding box of an extended fist.
 candidates=[]
 for y in range(b[1]+int((b[3]-b[1])*.39),b[1]+int((b[3]-b[1])*.56)):
  dark=[x for x in range(b[0],b[2]) if cell.getpixel((x,y))[3] and sum(cell.getpixel((x,y))[:3])<160]
  if dark:candidates.append((len(dark),statistics.mean(dark),y))
 best=sorted(candidates,reverse=True)[:5]
 pivot=statistics.mean(t[1] for t in best) if best else (b[0]+b[2])/2
 # Authored alignment correction: the bent airborne pose's dark hand was
 # mistaken for its belt by the automatic anchor detector.
 if i+1==75:pivot-=24/scale
 resized=cell.resize((round(cell.width*scale),round(cell.height*scale)),Image.Resampling.NEAREST)
 left=round(112-pivot*scale);top=round(142-b[3]*scale)
 # Never silently crop a foot, fist or head while packing the final atlas.
 assert left+b[0]*scale>=0 and left+b[2]*scale<=224,(i+1,'horizontal clipping')
 assert top+b[1]*scale>=0,(i+1,'vertical clipping')
 frame=Image.new('RGBA',(224,144));frame.alpha_composite(resized,(left,top))
 assert frame.getchannel('A').getbbox(),i
 frame.save(out/f'pose-{i+1:02d}.png')
 atlas.alpha_composite(frame,((i%4)*224,(i//4)*144))
 poses.append({'pose':i+1,'source_bounds':list(b),'belt_pivot':round(pivot,2),
               'game_bounds':list(frame.getchannel('A').getbbox()),'feet_y':142})
atlas.save(out/'fighter-right.png')
mirrored=Image.new('RGBA',atlas.size)
for i in range(len(cells)):
 frame=atlas.crop(((i%4)*224,(i//4)*144,(i%4+1)*224,(i//4+1)*144))
 mirrored.alpha_composite(ImageOps.mirror(frame),((i%4)*224,(i//4)*144))
mirrored.save(out/'fighter-left.png')
stage=HERE/'assets/source/dojo.png'
assert stage.exists(),'Copy the original generated dojo source first.'
Image.open(stage).convert('RGB').resize((384,224),Image.Resampling.LANCZOS).save(out/'dojo.png')
# Historical TIC bitmap font, MIT; graphics are shared glyph PNGs in both hosts.
font=(HERE/'assets/font.bin').read_bytes()
font_image=Image.new('RGBA',(570,6));d=ImageDraw.Draw(font_image)
for code in range(32,127):
 for y in range(6):
  for x in range(6):
   if font[code*8+y]&(1<<(7-x)):d.point(((code-32)*6+x,y),fill=(255,255,255,255))
font_image.save(out/'font.png')
shadow=Image.new('RGBA',(62,8));d=ImageDraw.Draw(shadow)
d.ellipse((0,0,61,7),fill=(69,77,50,255));d.ellipse((8,1,54,6),fill=(53,66,45,255))
shadow.save(out/'shadow.png')
report={'resolution':[384,224],'frame':[224,144],'frames':len(cells),'character_height':128,
 'sources':source_reports,'atlas_size':list(atlas.size),
 'atlas_decoded_bytes':atlas.width*atlas.height*4*2,'poses':poses,
 'notes':'Original art retained; binary alpha, per-sheet uniform scale, belt anchors; original kicks extracted by connected-figure ownership to recover the cross-cell mawashi foot. Poses require dojo review.'}
(HERE/'assets/import.json').write_text(json.dumps(report,indent=2)+'\n')
(HERE/'src/art.lua').write_text('return {frames=%d,width=%d,height=%d,bounds={%s}}\n'%(len(cells),*atlas.size,','.join('{'+','.join(map(str,p['game_bounds']))+'}' for p in poses)))
print('Imported',len(cells),'poses; decoded mirrored atlases:',report['atlas_decoded_bytes'],'bytes')
