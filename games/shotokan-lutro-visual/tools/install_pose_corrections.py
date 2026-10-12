"""Install only individually rejected poses; preserve every other runtime pixel."""
import argparse,json,shutil,io,time
from pathlib import Path
from PIL import Image
from sheet_cells import figures
from import_characters import binary,regions
from character_masks import belt_mask
HERE=Path(__file__).resolve().parents[1]
def save(im,path):
 stream=io.BytesIO();im.save(stream,format='PNG');raw=stream.getvalue()
 if path.exists() and path.read_bytes()==raw:return
 tmp=path.with_suffix('.png.tmp');tmp.write_bytes(raw)
 for attempt in range(25):
  try:tmp.replace(path);return
  except OSError:
   if attempt==24:raise
   time.sleep(.2)
def run(source,poses):
 dest=HERE/'assets/source/audit-corrections'/('poses-'+ '-'.join(map(str,poses))+'.png');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
 cells=figures(Image.open(dest).convert('RGBA'),len(poses),3,strict=False)
 masks_path=HERE/'assets/character-masks.json';masks=json.loads(masks_path.read_text())
 overrides_path=HERE/'assets/character-belt-overrides.json';overrides=json.loads(overrides_path.read_text())
 for row,body in enumerate(('adult','teen','child')):
  atlas_path=HERE/'docs'/f'character-{body}-atlas.png';atlas=Image.open(atlas_path).convert('RGBA')
  for col,pose in enumerate(poses):
   original=atlas.crop((((pose-1)%4)*224,((pose-1)//4)*144,((pose-1)%4+1)*224,((pose-1)//4+1)*144))
   backup=dest.parent/f'before-{body}-{pose}.png'
   if not backup.exists():original.save(backup)
   im=binary(cells[row*len(poses)+col]);ratio={'adult':129,'teen':111,'child':93}[body]/im.height
   if pose==75:
    # Airborne crouching never becomes a full standing-height fighter.
    from character_masks import hair_bounds
    from PIL import ImageFilter
    from character_masks import components
    from compile_character import layer_frames
    base_manifest=json.loads((HERE/'assets/character-assets.json').read_text())
    old_head=hair_bounds(layer_frames(body,'hair','default',base_manifest)[0])
    dark=Image.new('L',im.size)
    for yy in range(round(im.height*.14)):
     for xx in range(im.width):
      r,g,b,a=im.getpixel((xx,yy))
      if a and max(r,g,b)<95:dark.putpixel((xx,yy),255)
    core=dark.filter(ImageFilter.MinFilter(11)).filter(ImageFilter.MaxFilter(11))
    pixels=components(core)[0];new_head=(min(i%im.width for i in pixels),0,max(i%im.width for i in pixels)+1,0)
    ratio=(old_head[2]-old_head[0])/(new_head[2]-new_head[0])
   if pose==75:
    from import_characters import split
    for attempt in range(4):
     size=(round(im.width*ratio),round(im.height*ratio));trial=im.resize(size,Image.Resampling.NEAREST)
     canvas=Image.new('RGBA',(224,144));canvas.paste(trial,(112-trial.width//2,143-trial.height))
     measured=hair_bounds(split(canvas,regions(canvas))['hair'])
     width=measured[2]-measured[0];wanted=old_head[2]-old_head[0]
     if abs(width-wanted)<=1:break
     ratio*=wanted/width
   target=(round(im.width*ratio),round(im.height*ratio));im=im.resize(target,Image.Resampling.NEAREST)
   frame=Image.new('RGBA',(224,144));frame.paste(im,(112-im.width//2,143-im.height))
   save(frame,dest.parent/f'after-{body}-{pose}.png')
   index=pose-1;atlas.paste(frame,((index%4)*224,(index//4)*144))
   masks[body][str(pose)]=regions(frame);overrides.get(body,{}).pop(str(pose),None)
   cloth_path=HERE/'assets'/f'character-belt-{body}-mask.png';cloth=Image.open(cloth_path).convert('L');cloth.paste(belt_mask(frame),((index%4)*224,(index//4)*144));cloth.save(cloth_path)
   if body=='adult':save(frame,HERE/'src/assets'/f'pose-{pose:02}.png')
  atlas.save(atlas_path)
 masks_path.write_text(json.dumps(masks,indent=2)+'\n');overrides_path.write_text(json.dumps(overrides,indent=2)+'\n')
 manifest_path=HERE/'assets/pose-corrections.json';manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
 for body in ('adult','teen','child'):
  manifest.setdefault(body,{}).update({str(pose):f'assets/source/audit-corrections/after-{body}-{pose}.png' for pose in poses})
 manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--poses',default='51,55,59');a=p.parse_args();run(a.source,tuple(map(int,a.poses.split(','))))
