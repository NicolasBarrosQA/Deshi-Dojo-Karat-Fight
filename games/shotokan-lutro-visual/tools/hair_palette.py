"""Hair-only color material, baked on the developer machine, never at runtime."""
import colorsys,re
import numpy as np
from PIL import Image

COLORS={'original':None,'preto':'#211f20','castanho_escuro':'#493126','castanho':'#805037','castanho_claro':'#a77851','loiro':'#c5a05a','loiro_platinado':'#e9dfc7','ruivo':'#b85832','grisalho':'#96999d','branco':'#f3f3ef','azul':'#5078c4','verde':'#539772','roxo':'#8c62b2','rosa':'#ca789c'}

def valid(color):return color in COLORS or isinstance(color,str) and re.fullmatch(r'#[0-9a-fA-F]{6}',color) is not None

def target(color):
    value=COLORS.get(color,color)
    if value is None:return None
    return tuple(int(value[i:i+2],16) for i in (1,3,5))

def ramp(color):
    rgb=target(color)
    if rgb is None:return None
    h,l,s=colorsys.rgb_to_hls(*(c/255 for c in rgb))
    # White has gray contours, black has readable dark highlights. Both retain
    # the same authored luminance structure instead of a flat multiply filter.
    floor=.025+.19*l;ceiling=min(1,.18+.86*l)
    levels=np.linspace(floor,ceiling,8)
    return [tuple(round(c*255) for c in colorsys.hls_to_rgb(h,float(v),s*(.80 if v>.8 else 1))) for v in levels]

def recolor(image,color):
    shades=ramp(color)
    if shades is None:return image.copy()
    pixels=np.asarray(image).copy();rgb=pixels[:,:,:3].astype(float)
    luminance=rgb[:,:,0]*.2126+rgb[:,:,1]*.7152+rgb[:,:,2]*.0722
    # Brown source silhouettes have a consistent dark-ink -> lit-lock range.
    stops=np.array([8,22,38,58,81,108,139,183],dtype=float)
    for channel in range(3):pixels[:,:,channel]=np.rint(np.interp(luminance,stops,[r[channel] for r in shades])).astype('uint8')
    pixels[pixels[:,:,3]==0]=0
    return Image.fromarray(pixels)

def catalog():return [{'id':key,'swatch':value,'ramp':ramp(key)} for key,value in COLORS.items()]
