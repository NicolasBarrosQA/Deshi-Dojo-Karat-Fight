"""Reuse the new body's exact kamae at special guard endpoints.

Original preparation, execution, contact and reaction artwork is retained.
This is pose reuse and packing, never image deformation or invented animation.
"""
from PIL import Image,ImageOps
from avatar_set_import import ROOT,STAGE,DOCS,read,write
from compile_character import pack

def unpack(part):
    atlas=Image.open(STAGE/'assets'/(part['right']+'.png')).convert('RGBA');frames=[]
    for f in part['frames']:
        frame=Image.new('RGBA',(224,144));frame.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']));frames.append(frame)
    return frames

def main():
    bodies=read(STAGE/'character-assets.json');special=read(STAGE/'special-assets.json');changed=[]
    for body,b in bodies.items():
        guard=unpack(b['parts']['body']['default'])[0]
        cloth={name:unpack(part)[0] for name,part in b['parts']['belt'].items()}
        for group,a in special[body].items():
            indices=[8] if group in ('knockdown','ashi_finish') else [0,8]
            frames=unpack(a['body'])
            orient=group=='knockdown' and not a.get('ground_orientation')
            if orient:
                for i in (4,5,6):
                    frames[i]=ImageOps.mirror(frames[i]);l,t,r,bottom=a['bounds'][i];a['bounds'][i]=[224-r,t,224-l,bottom]
            for i in indices:frames[i]=guard.copy();a['bounds'][i]=b['bounds'][0]
            a['body']=pack(frames,'special-'+body+'-'+group,STAGE/'assets')
            for name,part in list(a['belts'].items()):
                frames=unpack(part)
                if orient:
                    for i in (4,5,6):frames[i]=ImageOps.mirror(frames[i])
                for i in indices:frames[i]=cloth[name].copy()
                a['belts'][name]=pack(frames,'special-'+body+'-'+group+'-belt-'+name,STAGE/'assets')
            a['guard_reference']={'body':body,'pose':1,'frames':[i+1 for i in indices]}
            if orient:a['ground_orientation']='Authored lying poses selected in opposite direction to keep head-left/feet-right through the backward fall; the player-facing mirror remains applied normally.'
            changed.append({'body':body,'group':group,'frames':[i+1 for i in indices]})
    write(STAGE/'special-assets.json',special)
    write(DOCS/'guard-continuity.json',{'purpose':'Exact new-body kamae at return to guard, avoiding a silhouette change when switching back to the normal repertoire. Authored execution/reaction frames unchanged.','bindings':changed})
    print('Normalized guard endpoints in',len(changed),'animations using the new neutral bodies.')

if __name__=='__main__':main()
