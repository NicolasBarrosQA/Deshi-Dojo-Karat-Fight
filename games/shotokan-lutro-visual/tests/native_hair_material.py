"""Authoring highlights must not become bald holes during material extraction."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from native_hair_material import PAINT_COLORS,mask,extract
colors=[tuple(int(c[i:i+2],16) for i in (1,3,5))+(255,) for c in PAINT_COLORS]
other=[(232,165,110,255),(220,224,228,255),(35,35,35,255),(0,255,0,0)]
pixels=np.array([colors+other],dtype='uint8');found=mask(pixels)
assert found[0,:5].all(),'Declared light and dark hair tones must all survive'
assert not found[0,5:].any(),'Skin, gi, ink and transparency must not become hair'
for color in ['castanho_escuro','branco','preto']:
    result=np.asarray(extract(Image.fromarray(pixels),color));assert (result[0,:5,3]==255).all();assert (result[0,5:]==0).all()
print('PASS every declared material shade preserved; skin and gi untouched')
