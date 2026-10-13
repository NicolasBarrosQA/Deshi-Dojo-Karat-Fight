"""Actual baked layers: pose coverage, limb depth, palettes and body isolation."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from prepare_hair_bindings import animations
from hair_art import apply,overlay,read,PAD
from bake_native_hair import foreground,rotation
from head_registration import skin_mask
from compile_character import transform
poses=animations();bindings=read('hair-bindings.json');fits=json.loads((ROOT/'docs/hair-rebuild-v2/native-pose-registration.json').read_text());count=0;gaps=[]
for style in ('masculino_curto','feminino_chanel'):
    for body,groups in poses.items():
        for group,frames in groups.items():
            assert len(read('native-hair-poses.json')['styles'][style][body]['groups'][group])==len(frames)
            for i,base in enumerate(frames):
                student={'body':body,'hair':style,'appearance':{'hair_color':'original'}}
                layer=overlay(student,group,i);mask=np.asarray(layer)[:,:,3]>0;b=layer.getbbox();assert b and b[0]>=0 and b[2]<=224 and b[1]>=0 and b[3]<=168
                assert set(np.unique(np.asarray(layer)[:,:,3]))<={0,255}
                protect=foreground(bindings[body][group][i]);assert not np.any(mask[PAD:]&protect),'Hair covers authored foreground'
                result=np.asarray(apply(base,student,group,i));original=np.asarray(base)
                assert np.array_equal(result[PAD:][~mask[PAD:]],original[~mask[PAD:]]),'Body changed outside hair'
                assert np.array_equal(result[PAD:][protect],original[protect]),'Raised arm changed'
                fit=fits[body][group][i];yy,xx=np.indices((144,224));local=np.stack([xx-fit['center'][0],yy-fit['center'][1]],axis=-1)@rotation(fit['angle'])
                assert not np.any(mask[PAD:]&((abs(local[:,:,0])>30)|(abs(local[:,:,1])>32))),(style,body,group,i+1,'Hair detached from head',b,fit)
                for color in ('preto','branco','#a54f22'):
                    other=overlay({**student,'appearance':{'hair_color':color}},group,i)
                    assert np.array_equal(np.asarray(other)[:,:,3]>0,mask),'Color changed the hair silhouette'
                for height,build in ((.94,'leve'),(1.,'medio'),(1.04,'forte')):
                    transformed=transform(Image.fromarray(result),{'height':height,'build':build},base.getbbox())
                    bbox=transformed.getbbox();assert bbox and bbox[0]>=0 and bbox[2]<=224 and bbox[3]<=168
                count+=1
print('PASS',count,'baked poses; binary alpha, limb depth, body isolation, four palettes, three proportions, fixed logical canvas')
