"""Every hair/beard pair: bangs stay in front, with contrasting materials."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from prepare_hair_bindings import animations
from hair_art import apply,overlay,styles,beards,read,PAD
poses=animations();cases=overlapping=0
for hair in styles():
    for beard in beards():
        for body,groups in poses.items():
            student={'body':body,'hair':hair,'beard':beard,'appearance':{'hair_color':'branco','beard_color':'preto'}}
            for group,index in [('base',0),('base',8),('base',14),('base',58),('base',61),('base',84),('knockdown',4),('knockdown',5)]:
                frame=groups[group][index];h=np.asarray(overlay(student,group,index));b=np.asarray(overlay(student,group,index,'beard'))
                mask=(h[:,:,3]>0)&(b[:,:,3]>0);binding=read('hair-bindings.json')[body][group][index]
                for y,start,end in binding['foreground_runs']:mask[y+PAD,start:end]=False
                for x,y in binding.get('foreground_points',[]):mask[y+PAD,x]=False
                result=np.asarray(apply(frame,student,group,index));assert np.array_equal(result[mask],h[mask]),(body,hair,beard,group,index,'beard painted over bangs')
                cases+=1;overlapping+=bool(np.any(mask))
        print(hair,beard,cases,flush=True)
assert overlapping>0,'Fixtures must exercise actual hair/beard overlap'
report={'hair_beard_pairs':len(styles())*len(beards()),'layered_pose_cases':cases,'actual_overlap_cases':overlapping,'contrasting_materials':'white hair, black beard','errors':0}
(ROOT/'docs/hair-catalog/layer-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
