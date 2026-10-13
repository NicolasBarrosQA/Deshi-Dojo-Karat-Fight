"""Unpublished single-view art study on actual approved guard sprites."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import hair_art
from prepare_hair_bindings import animations

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'assets/source/hair-revision-v1/01-rabo-baixo-three-quarter.png'
with Image.open(source) as im:w,h=im.size
view={'path':source.relative_to(ROOT).as_posix(),'center':[260*w/512,270*h/512],'width':340*w/512,'height':380*h/512}
original_styles=hair_art.styles()
hair_art.styles=lambda:{**original_styles,'revision_pilot':{'label':'Estudo de rabo baixo','views':{'three_quarter':view}}}
frames=animations();sheet=Image.new('RGB',(896,644),'#243640');draw=ImageDraw.Draw(sheet)
checks=[]
for col,(body,label) in enumerate([('child_female','CRIANCA'),('adult_female','ADULTA')]):
    student={'body':body,'hair':'revision_pilot','appearance':{'hair_color':'original'}}
    frame=frames[body]['base'][0];hair=hair_art.overlay(student,'base',0);result=hair_art.apply(frame,student,'base',0)
    src=np.asarray(frame);out=np.asarray(result)[hair_art.PAD:];coverage=np.asarray(hair)[hair_art.PAD:,:,3]>0
    assert np.array_equal(src[~coverage],out[~coverage]),'Body pixels outside hair must remain original'
    x=col*448;draw.text((x+20,12),label+' - SPRITE ORIGINAL + NOVO ESTUDO',fill='#eccb91')
    enlarged=result.resize((448,336),Image.Resampling.NEAREST);sheet.paste(enlarged,(x,35),enlarged)
    draw.text((x+20,378),'DETALHE AMPLIADO SEM SUAVIZACAO',fill='#eccb91')
    cx,cy=hair_art.read('hair-bindings.json')[body]['base'][0]['center']
    crop=result.crop((round(cx)-26,round(cy)+hair_art.PAD-25,round(cx)+26,round(cy)+hair_art.PAD+31)).resize((208,224),Image.Resampling.NEAREST)
    sheet.paste(crop,(x+120,404),crop);checks.append({'body':body,'outside_hair_unchanged':True})
folder=ROOT/'docs/hair-revision-v1';folder.mkdir(exist_ok=True);sheet.save(folder/'01-rabo-baixo-aplicado.png')
(folder/'status.json').write_text(json.dumps({'status':'unapproved_art_study','views_authored':1,'poses_previewed':['guard'],'registration_reference':'approved curto_classico three_quarter','checks':checks},indent=2)+'\n')
print('Unpublished guard study rendered on approved child and adult sprites')
