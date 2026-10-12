"""Validated roster configuration; no combat rules or image dependencies."""
import hashlib,json,re
from pathlib import Path

from skin_palette import PALETTES,catalog as skin_catalog
SKINS={key:entry['swatch'] if entry['ramp'] is not None else None for key,entry in PALETTES.items()}
from hair_palette import COLORS,valid as valid_hair_color,target as hair_target,catalog as hair_palette_catalog
HAIR_COLORS={key:hair_target(key) for key in COLORS}
HEIGHTS=[.94,1,1.04]
BUILDS={'leve':.94,'medio':1,'forte':1.06}
DEFAULT={'skin':'original','hair_color':'original','height':1,'build':'medio','emblem':'nenhum'}

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def write(path,value):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(path)
def validate(value,config,manifest):
    if not isinstance(value,dict):raise ValueError('O personagem deve ser um objeto JSON.')
    allowed={'id','name','nickname','body','belt','face','hair','beard','identity','appearance','visual','portrait'}
    if set(value)-allowed:raise ValueError('Campos desconhecidos: '+', '.join(sorted(set(value)-allowed)))
    result={k:value.get(k,'default') for k in ('face','hair')}
    for k in ('id','name','body','belt'):result[k]=value.get(k)
    if not isinstance(result['id'],str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,47}',result['id']):raise ValueError('ID: use de 1 a 48 letras minusculas, numeros, - ou _.')
    for field in ('name','nickname'):
        text=value.get(field,'')
        if not isinstance(text,str) or len(text)>32 or any(ord(c)<32 or c in '<>' for c in text):raise ValueError('Nome e apelido: ate 32 caracteres, sem controles ou marcacao HTML.')
        result[field]=text.strip()
    if not result['name']:raise ValueError('Informe o nome do personagem.')
    if not isinstance(result['body'],str) or result['body'] not in manifest:raise ValueError('Modelo corporal inexistente.')
    identity=value.get('identity','default')
    if identity!='default':
        identities_path=Path(__file__).resolve().parents[1]/'assets/character-identities.json'
        identities=read(identities_path) if identities_path.exists() else {'bodies':{}}
        if not isinstance(identity,str) or identity not in identities['bodies'].get(result['body'],{}):raise ValueError('Identidade artistica indisponivel para este corpo.')
        if result['face']!='default' or result['hair']!='default':raise ValueError('Esta identidade usa um conjunto proprio de rosto e cabelo.')
        result['identity']=identity
    if not isinstance(result['belt'],str) or result['belt'] not in config['belts']:raise ValueError('Faixa inexistente.')
    for layer in ('face','hair'):
        available=manifest[result['body']]['parts'][layer]
        if layer=='hair':
            from hair_art import styles
            available={**available,**styles()}
        if not isinstance(result[layer],str) or result[layer] not in available:raise ValueError('Asset de '+layer+' inexistente para este corpo.')
    from hair_art import beards
    beard=value.get('beard','default')
    if not isinstance(beard,str) or (beard!='default' and beard not in beards()):raise ValueError('Asset de barba inexistente.')
    if beard!='default':result['beard']=beard
    appearance=value.get('appearance',{})
    if not isinstance(appearance,dict) or set(appearance)-set(DEFAULT)-{'beard_color'}:raise ValueError('Configuracao de aparencia invalida.')
    appearance={**DEFAULT,**appearance}
    choices={'skin':SKINS,'hair_color':HAIR_COLORS,'height':HEIGHTS,'build':BUILDS,'emblem':['nenhum','dojo']}
    for key,options in choices.items():
        if key=='hair_color' and isinstance(appearance[key],str) and valid_hair_color(appearance[key]):
            if appearance[key].startswith('#'):appearance[key]=appearance[key].lower()
            continue
        if isinstance(appearance[key],(dict,list,bool)) or appearance[key] not in options:raise ValueError('Opcao de '+key+' indisponivel.')
    if 'beard_color' in appearance:
        if not isinstance(appearance['beard_color'],str) or not valid_hair_color(appearance['beard_color']):raise ValueError('Cor de barba invalida.')
        appearance['beard_color']=appearance['beard_color'].lower()
        if appearance['beard_color']=='original':appearance.pop('beard_color')
    result['appearance']=appearance
    return result
def visual_key(student):
    data={k:student[k] for k in ('body','face','hair','appearance')}
    if student.get('identity','default')!='default':data['identity']=student['identity']
    if student.get('beard','default')!='default':data['beard']=student['beard']
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()[:16]
def catalog(config,manifest):
    path=Path(__file__).resolve().parents[1]/'assets/character-identities.json'
    identities=read(path)['bodies'] if path.exists() else {}
    neutral=all(b.get('revision')=='neutral-2d-v3' for b in manifest.values())
    from hair_art import styles,beards
    hair_styles=styles()
    return {'bodies':config['body_order'],'belts':config['belt_order'],'skins':list(SKINS),'hair_colors':list(HAIR_COLORS),'heights':HEIGHTS,'builds':list(BUILDS),'emblems':['nenhum','dojo'],
            'neutral_bases':neutral,
            'skin_palettes':skin_catalog(),'creator_only':True,
            'hair_styles':[{'id':'default','label':'Sem cabelo','category':'neutro'},*[{'id':key,'label':value['label'],'category':value.get('category','masculino')} for key,value in hair_styles.items()]],'hair_palettes':hair_palette_catalog(),
            'beard_styles':[{'id':'default','label':'Sem barba'},*[{'id':key,'label':value['label']} for key,value in beards().items()]],
            'identities':{body:[{'id':'default','label':'Base neutra aprovada' if neutral else 'Personagem original'},*[{'id':key,'label':entry['label'],'thumbnail':'identity-thumbnail-'+body+'-'+key} for key,entry in identities.get(body,{}).items()]] for body in config['body_order']},
            'parts':{b:{p:list(v['parts'][p])+([] if p!='hair' else list(hair_styles)) for p in ('face','hair')} for b,v in manifest.items()},
            'art_note':'Seis bases 2D aprovadas. Cabelos e barbas preparados por pose, com cores independentes da pele. Rostos ainda neutros. Personalizacao no computador; personagens exportados prontos para o fliperama.' if neutral else 'Bases corporais com cabelos e cores preparados antes da exportacao.'}
