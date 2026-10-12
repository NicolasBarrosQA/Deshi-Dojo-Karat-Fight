"""Attach authored reusable face/hair views without re-exporting body art.

Usage: python tools/import_identity.py --body child --layer hair --id short
       --sheet assets/source/short-hair.png --mapping assets/short-hair.json
Mapping: {"views":{"right":[x,y,w,h],"rear":[x,y,w,h]},
          "poses":[{"view":"right","dx":0,"dy":0}, ... exactly 92 entries]}
Coordinates are pixels. No artistic edits: crop, anchor and mirror only.
"""
import argparse,json
from pathlib import Path
from PIL import Image
from import_characters import HERE,pack,binary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--body',choices=json.loads((HERE/'assets/characters.json').read_text())['body_order'],required=True)
    p.add_argument('--layer',choices=['face','hair'],required=True)
    p.add_argument('--id',required=True);p.add_argument('--sheet',type=Path,required=True)
    p.add_argument('--mapping',type=Path,required=True);a=p.parse_args()
    assert a.id.isascii() and all(c.isalnum() or c in '-_' for c in a.id) and a.id!='default','Use a new ASCII asset ID'
    manifest_path=HERE/'assets/character-assets.json'
    manifest=json.loads(manifest_path.read_text());body=manifest[a.body]
    mapping=json.loads(a.mapping.read_text());assert len(mapping['poses'])==92
    sheet=binary(Image.open(a.sheet));frames=[]
    for pose,entry in enumerate(mapping['poses']):
        if entry.get('view') is None:
            frames.append(Image.new('RGBA',(224,144)))
            continue
        rect=mapping['views'][entry['view']];x,y,w,h=rect
        assert x>=0 and y>=0 and w>0 and h>0 and x+w<=sheet.width and y+h<=sheet.height
        crop=sheet.crop((x,y,x+w,y+h));anchor=body['parts'][a.layer]['default']['frames'][pose]
        # Center shared views over each original attachment, keeping per-pose edits optional.
        px=round(anchor['x']+(anchor['w']-w)/2)+entry.get('dx',0)
        py=anchor['y']+entry.get('dy',0)
        assert px>=0 and py>=0 and px+w<=224 and py+h<=144,(pose,'clipped attachment')
        frame=Image.new('RGBA',(224,144));frame.paste(crop,(px,py));frames.append(frame)
    body['parts'][a.layer][a.id]=pack(a.body,a.layer,a.id,frames)
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    print('Imported identity part; run tools/build.py. Bodies, combat and pose IDs unchanged.')

if __name__=='__main__':main()
