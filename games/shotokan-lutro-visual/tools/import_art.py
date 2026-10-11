"""Import generated reference art into fixed, foot-aligned game cells.

Mechanical atlas packing/downsampling only: original high-resolution art retained.
No procedural replacement of the authored character or scene.
"""
from pathlib import Path
import hashlib,json,statistics
from PIL import Image,ImageDraw,ImageOps
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[1]
out=HERE/'src/assets';out.mkdir(parents=True,exist_ok=True)
sources=[('karateca-sheet.png',4,3),('defenses.png',3,4),('kicks.png',4,3),('punches.png',4,2)]
cells=[];source_reports=[]
for filename,cols,rows in sources:
 source=HERE/'assets/source'/filename
 sheet=Image.open(source).convert('RGBA');group=[]
 for row in range(rows):
  for col in range(cols):
   cell=sheet.crop((round(col*sheet.width/cols),round(row*sheet.height/rows),round((col+1)*sheet.width/cols),round((row+1)*sheet.height/rows)))
   alpha=cell.getchannel('A').point(lambda v:255 if v>=128 else 0)
   cell.putalpha(alpha);bounds=alpha.getbbox();assert bounds,(filename,row,col)
   group.append((cell,bounds))
 scale=128/statistics.median(b[3]-b[1] for _,b in group)
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
 resized=cell.resize((round(cell.width*scale),round(cell.height*scale)),Image.Resampling.NEAREST)
 left=round(112-pivot*scale);top=round(142-b[3]*scale)
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
 'notes':'Original art retained; binary alpha, per-sheet uniform scale and belt anchors; poses require dojo review.'}
(HERE/'assets/import.json').write_text(json.dumps(report,indent=2)+'\n')
(HERE/'src/art.lua').write_text('return {frames=%d,width=%d,height=%d}\n'%(len(cells),*atlas.size))
print('Imported',len(cells),'poses; decoded mirrored atlases:',report['atlas_decoded_bytes'],'bytes')
