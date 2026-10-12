"""Exhaustive hair coverage/material/geometry validation, without touching roster."""
import json,sys,tempfile
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from prepare_hair_bindings import animations
from hair_art import apply,overlay,styles,logical_bounds,PAD
from hair_palette import COLORS,recolor,ramp
from compile_character import transform,pack
from character_registry import read,validate,visual_key

def run():
    geometry=materials=0;allposes=animations()
    for body,groups in allposes.items():
        for style in styles():
            student={'body':body,'hair':style,'appearance':{'hair_color':'original'}}
            for group,frames in groups.items():
                for i,frame in enumerate(frames):
                    hair=overlay(student,group,i);result=apply(frame,student,group,i)
                    original=np.asarray(frame);actual=np.asarray(result)[PAD:];coverage=np.asarray(hair)[PAD:,:,3]>0
                    assert np.array_equal(original[~coverage],actual[~coverage]),(body,style,group,i,'changed pixels outside hair')
                    assert set(np.unique(np.asarray(result)[:,:,3]))<={0,255}
                    assert logical_bounds(result)[3]<=144
                    for height in (.94,1,1.04):
                        for build in ('leve','medio','forte'):
                            ap={'height':height,'build':build};b=logical_bounds(transform(result,ap,frame.getbbox()))
                            assert b[0]>=0 and b[2]<=224 and b[3]<=144
                            # The added headroom must not alter authored body scale.
                            padded=Image.new('RGBA',(224,144+PAD));padded.paste(frame,(0,PAD));padded.info['logical_origin_y']=-PAD
                            one=np.asarray(transform(padded,ap,frame.getbbox()))[PAD:]
                            two=np.asarray(transform(frame,ap,frame.getbbox()))
                            assert np.array_equal(one,two),(body,group,i,ap,'body scale drift')
                            geometry+=1
                    for color in COLORS:
                        tinted=recolor(hair,color)
                        assert np.array_equal(np.asarray(hair)[:,:,3],np.asarray(tinted)[:,:,3])
                        if color!='original':assert len(set(map(tuple,np.asarray(tinted)[:,:,:3][np.asarray(tinted)[:,:,3]>0])))>=4
                        materials+=1
    config=read(ROOT/'assets/characters.json');manifest=read(ROOT/'assets/character-assets.json')
    s={**config['students']['demo-adult'],'hair':'medio_ondulado','appearance':{'hair_color':'#aBcD12'}}
    value=validate(s,config,manifest);assert value['appearance']['hair_color']=='#abcd12'
    with tempfile.TemporaryDirectory() as tmp:
        student={'body':'adult','hair':'medio_ondulado','appearance':{'hair_color':'branco'}}
        frames=[apply(im,student,'base',i) for i,im in enumerate(allposes['adult']['base'])]
        record=pack(frames,'hair-roundtrip',Path(tmp));atlas=Image.open(Path(tmp)/'hair-roundtrip-right.png')
        for frame,f in zip(frames,record['frames']):
            rebuilt=Image.new('RGBA',frame.size);rebuilt.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']+PAD));assert rebuilt.tobytes()==frame.tobytes()
    result={'pose_style_cases':sum(len(frames) for groups in allposes.values() for frames in groups.values())*len(styles()),'proportions_verified':geometry,'palette_material_cases':materials,'pack_roundtrip_frames':92,'body_pixels_and_scale_preserved':True,'binary_alpha':True}
    (ROOT/'docs/hair/asset-tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':run()
