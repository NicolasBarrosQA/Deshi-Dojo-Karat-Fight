"""Visual-counterexample contracts; these fail the previous joined-skin mapping."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from hair_art import apply,read,PAD,overlay
from head_registration import skin_mask
from prepare_hair_bindings import animations
from skin_palette import apply_skin_palette,PALETTES

poses=animations();bindings=read('hair-bindings.json')
# Coordinates reviewed on the original bald anatomy, independent of the fitter.
landmarks={'adult':(115,25),'adult_female':(110,24),'teen':(116,41),'teen_female':(112,42),'child':(114,61),'child_female':(112,61)}
for body,(cx,cy) in landmarks.items():
    binding=bindings[body]['base'][0]
    assert abs(binding['center'][0]-cx)<2 and abs(binding['center'][1]-cy)<2,(body,'guard scalp drift')
    assert 17<binding['width']<25
    original=poses[body]['base'][0];rows,cols=np.indices((144,224))
    for style in ('curto_classico','medio_ondulado','crespo_curto'):
        student={'body':body,'hair':style,'appearance':{'hair_color':'grisalho'}}
        hair=np.asarray(overlay(student,'base',0))[PAD:]
        scalp=skin_mask(original)&(rows<cy-3)&(np.abs(cols-cx)<14)&(hair[:,:,3]>0)
        assert np.count_nonzero(scalp)>10
        for skin in PALETTES:
            result=np.asarray(apply(apply_skin_palette(original,skin),student,'base',0))[PAD:]
            assert np.array_equal(result[scalp],hair[scalp]),(body,style,skin,'bald scalp restored through hair')
binding=bindings['adult']['base'][14]
assert abs(binding['center'][0]-115)<2 and abs(binding['center'][1]-23)<2,'Raised forearm mistaken for skull'
assert 17<=binding['width']<=21,'Raised forearm enlarges hair'
# This forearm polygon is traced on the exact pose attached in the bug report.
mask=Image.new('L',(224,144));ImageDraw.Draw(mask).polygon([(114,6),(118,6),(142,18),(139,23),(120,14),(110,11)],fill=255)
frame=poses['adult']['base'][14];pixels=np.asarray(frame);valid=(np.asarray(mask)>0)&(pixels[:,:,3]>0)
for style in ('curto_classico','medio_ondulado','crespo_curto'):
    for skin in ('original','clara','retinta'):
        source=apply_skin_palette(frame,skin)
        student={'body':'adult','hair':style,'appearance':{'hair_color':'grisalho'}}
        output=np.asarray(apply(source,student,'base',14))[PAD:]
        assert np.array_equal(output[valid],np.asarray(source)[valid]),(style,skin,'hair painted on raised forearm')
print('PASS six independently reviewed guard anchors; reported forearm pose preserved for all cuts and skin extremes')
(ROOT/'docs/hair/fit-regression.json').write_text(json.dumps({'independent_guard_landmarks':6,'crown_coverage_cases':216,'reported_pose_15_forearm_cases':9,'previous_mapping_rejected':True},indent=2)+'\n')
