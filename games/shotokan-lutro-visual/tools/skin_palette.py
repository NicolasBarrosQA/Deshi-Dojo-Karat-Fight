"""Developer-only skin material ramps; runtime receives finished PNGs.

Source coverage is derived once from the neutral artwork. Recoloring preserves
pixel positions, alpha and ink, and blends only the original antialias fringe.
No resizing, blur, shader or whole-character tint is used.
"""
VERSION='skin-material-v1'
LEVELS=(0,50,90,130,170,210,255)
def tone(label,undertone,colors):return {'label':label,'undertone':undertone,'ramp':colors,'swatch':colors[4]}
PALETTES={
 'original':{'label':'Original da arte','undertone':'Preserva os pixels aprovados','ramp':None,'swatch':[238,177,130]},
 'porcelana':tone('Porcelana','Neutro',[(44,30,29),(88,59,53),(132,95,82),(186,143,124),(234,195,171),(250,220,199),(255,240,224)]),
 'clara':tone('Clara','Neutro',[(38,25,25),(79,47,40),(125,81,64),(176,126,99),(224,174,136),(245,207,172),(255,235,211)]),
 'clara_quente':tone('Clara dourada','Quente',[(38,25,20),(80,48,32),(126,83,51),(181,132,86),(229,181,124),(250,214,163),(255,240,204)]),
 'clara_oliva':tone('Clara oliva','Oliva',[(34,27,22),(72,54,38),(115,89,61),(162,133,91),(205,174,124),(235,209,164),(252,238,204)]),
 'media':tone('Média neutra','Neutro',[(31,21,20),(65,39,32),(104,64,48),(146,96,71),(189,132,98),(221,171,131),(246,211,173)]),
 'media_quente':tone('Média dourada','Quente',[(31,20,17),(68,40,27),(108,69,42),(151,106,63),(196,148,92),(226,186,130),(249,220,174)]),
 'media_oliva':tone('Média oliva','Oliva',[(29,23,18),(60,46,31),(96,75,47),(137,112,72),(178,151,102),(210,187,139),(238,218,177)]),
 'morena':tone('Morena bronze','Quente',[(27,18,16),(58,32,24),(94,54,35),(132,81,52),(173,114,76),(206,151,108),(237,193,150)]),
 'castanha':tone('Castanha','Neutro',[(23,16,16),(49,28,24),(80,45,35),(112,67,50),(148,96,72),(184,132,101),(220,175,139)]),
 'escura':tone('Escura','Neutro',[(18,13,14),(37,22,21),(62,36,30),(90,54,43),(120,77,59),(154,109,85),(197,152,121)]),
 'retinta':tone('Retinta','Neutro quente',[(14,10,12),(25,16,16),(41,25,22),(60,38,31),(82,54,42),(114,80,61),(161,122,96)])
}
def catalog():return [{'id':key,**entry} for key,entry in PALETTES.items()]
def skin_coverage(frame):
    import numpy as np
    px=np.asarray(frame).astype(np.float32);r,g,b,a=[px[:,:,i] for i in range(4)]
    warm=(a>0)&(r>55)&(r>g*1.055)&(g>b*1.015)&(r-b>16)
    saturation=(r-b)/np.maximum(r,1)
    coverage=np.clip((saturation-.08)/.18,0,1)*warm
    return coverage
def palette_lut(key):
    import numpy as np
    ramp=PALETTES[key]['ramp'];assert ramp is not None
    values=np.arange(256)
    return np.stack([np.interp(values,LEVELS,[color[c] for color in ramp]) for c in range(3)],axis=1)
def apply_skin_palette(frame,key):
    if key=='original':return frame.copy()
    import numpy as np
    from PIL import Image
    original=np.asarray(frame);rgb=original[:,:,:3].astype(np.float32)
    luminance=np.rint(rgb[:,:,0]*.2126+rgb[:,:,1]*.7152+rgb[:,:,2]*.0722).astype(np.uint8)
    coverage=skin_coverage(frame)[:,:,None]
    mapped=palette_lut(key)[luminance]
    result=original.copy();result[:,:,:3]=np.rint(rgb*(1-coverage)+mapped*coverage).clip(0,255).astype(np.uint8)
    return Image.fromarray(result)
