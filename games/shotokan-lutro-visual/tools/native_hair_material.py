"""Read the explicit green authoring material, including its lightest shade."""
import numpy as np
from PIL import Image
from hair_palette import recolor

PAINT_COLORS=['#103510','#245e24','#438b43','#70b870','#a4d4a4']

def mask(pixels):
    p=np.asarray(pixels).astype(float);r,g,b,a=[p[:,:,i] for i in range(4)]
    return (a>=128)&(g>r*1.06)&(g>b*1.06)&(g>12)

def extract(image,color='castanho_escuro'):
    p=np.asarray(image.convert('RGBA')).copy();visible=mask(p)
    value=np.rint(np.max(p[:,:,:3],axis=2).astype(float)*183/255).astype('uint8')
    for channel in range(3):p[:,:,channel]=value
    p[:,:,3]=visible*255;p[~visible]=0
    return recolor(Image.fromarray(p),color)
