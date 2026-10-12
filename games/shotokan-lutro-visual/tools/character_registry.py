"""Validated roster configuration; no combat rules or image dependencies."""
import hashlib,json,re
from pathlib import Path

from skin_palette import PALETTES,catalog as skin_catalog
SKINS={key:entry['swatch'] if entry['ramp'] is not None else None for key,entry in PALETTES.items()}
HAIR_COLORS={'original':None,'preto':[35,32,30],'castanho':[83,48,27],'loiro':[172,134,64],'ruivo':[133,57,30],'grisalho':[135,139,142]}
HEIGHTS=[.94,1,1.04]
BUILDS={'leve':.94,'medio':1,'forte':1.06}
DEFAULT={'skin':'original','hair_color':'original','height':1,'build':'medio','emblem':'nenhum'}

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def write(path,value):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(path)
def validate(value,config,manifest):
    if not isinstance(value,dict):raise ValueError('O personagem deve ser um objeto JSON.')
    allowed={'id','name','nickname','body','belt','face','hair','identity','appearance','visual','portrait'}
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
        if not isinstance(result[layer],str) or result[layer] not in manifest[result['body']]['parts'][layer]:raise ValueError('Asset de '+layer+' inexistente para este corpo.')
    appearance=value.get('appearance',{})
    if not isinstance(appearance,dict) or set(appearance)-set(DEFAULT):raise ValueError('Configuracao de aparencia invalida.')
    appearance={**DEFAULT,**appearance}
    choices={'skin':SKINS,'hair_color':HAIR_COLORS,'height':HEIGHTS,'build':BUILDS,'emblem':['nenhum','dojo']}
    for key,options in choices.items():
        if isinstance(appearance[key],(dict,list,bool)) or appearance[key] not in options:raise ValueError('Opcao de '+key+' indisponivel.')
    result['appearance']=appearance
    return result
def visual_key(student):
    data={k:student[k] for k in ('body','face','hair','appearance')}
    if student.get('identity','default')!='default':data['identity']=student['identity']
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()[:16]
def catalog(config,manifest):
    path=Path(__file__).resolve().parents[1]/'assets/character-identities.json'
    identities=read(path)['bodies'] if path.exists() else {}
    neutral=all(b.get('revision')=='neutral-2d-v3' for b in manifest.values())
    return {'bodies':config['body_order'],'belts':config['belt_order'],'skins':list(SKINS),'hair_colors':list(HAIR_COLORS),'heights':HEIGHTS,'builds':list(BUILDS),'emblems':['nenhum','dojo'],
            'neutral_bases':neutral,
            'skin_palettes':skin_catalog(),'creator_only':True,
            'identities':{body:[{'id':'default','label':'Base neutra aprovada' if neutral else 'Personagem original'},*[{'id':key,'label':entry['label'],'thumbnail':'identity-thumbnail-'+body+'-'+key} for key,entry in identities.get(body,{}).items()]] for body in config['body_order']},
            'parts':{b:{p:list(v['parts'][p]) for p in ('face','hair')} for b,v in manifest.items()},
            'art_note':'Seis bases neutras em 2D: crianca, adolescente e adulto, masculinos e femininos, com suas animacoes de combate. Rosto e cabelo ainda nao definidos.' if neutral else 'Ha bases corporais masculinas e femininas proprias para crianca, adolescente e adulto. Cada base tem suas poses de golpes, saltos e quedas. As identidades adicionais de rosto e cabelo aparecem quando compativeis com o corpo escolhido.'}
