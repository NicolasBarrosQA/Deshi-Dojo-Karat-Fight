"""Distinct everyday haircut and facial hair authoring briefs."""
import json
from pathlib import Path

MALE = [
    ('buzz_uniforme', 'Buzz uniforme', 'uniform close buzz cut with fine visible bristle texture'),
    ('crew_cut', 'Crew cut', 'short upright flat crew cut, neatly tapered temples'),
    ('caesar', 'Caesar', 'short textured Caesar with straight tiny fringe'),
    ('french_crop', 'French crop', 'heavy textured French crop with thick blunt forward fringe'),
    ('risca_lateral', 'Risca lateral', 'classic side parted medium hair with polished comb ridges'),
    ('cortina_curta', 'Cortina curta', 'short center parted curtain fringe at brow height'),
    ('franja_lateral', 'Franja lateral', 'asymmetric long diagonal fringe with compact short back'),
    ('cacheado_taper', 'Cacheado taper', 'tight small curls atop neatly tapered sides'),
    ('cacheado_medio', 'Cacheado médio', 'round ear length loose curly mop, separated ringlets'),
    ('afro_redondo', 'Afro redondo', 'compact perfectly rounded dense afro silhouette'),
]

FEMALE = [
    ('coque_trancado_baixo', 'Coque trançado baixo', 'neat center-part crown, two fine side braids merging into a compact low nape bun'),
    ('pixie_classico', 'Pixie clássico', 'very short feminine pixie with tapered nape and tiny soft side fringe'),
    ('pixie_longo', 'Pixie longo', 'long asymmetric pixie fringe sweeping one brow and compact tapered back'),
    ('bob_reto', 'Bob reto', 'precise chin length straight bob with center part and blunt ends'),
    ('bob_franja', 'Bob com franja', 'compact chin length bob with dense straight brow fringe'),
    ('bob_ondulado', 'Bob ondulado', 'chin length soft S wave bob with off center part'),
    ('bob_cacheado', 'Bob cacheado', 'chin length springy ringlet bob with rounded volume'),
    ('coque_bailarina', 'Coque bailarina', 'sleek crown with perfectly circular compact ballet bun high at rear'),
    ('rabo_alto_curto', 'Rabo alto curto', 'high tied ponytail with a short fan of hair ending above nape'),
    ('rabo_baixo_curto', 'Rabo baixo curto', 'low tied short ponytail compact behind neck'),
]

BEARDS = [
    ('barba_sombra', 'Barba curta', 'fine dense close cropped full stubble following jaw and mustache'),
    ('barba_cheia', 'Barba cheia', 'neat compact full beard, connected mustache, rounded jaw silhouette'),
    ('barba_quadrada', 'Barba quadrada', 'short boxed beard with crisp squared lower chin and tapered cheek line'),
    ('cavanhaque', 'Cavanhaque', 'connected compact mustache and chin goatee, clean cheeks'),
    ('van_dyke', 'Van Dyke', 'separate slender mustache and pointed small chin beard, clean cheeks'),
    ('bigode', 'Bigode', 'neat thick classic mustache only, no cheek or chin beard'),
]

def plan():
    assert len(MALE)==10 and len(FEMALE)==10 and len(BEARDS)==6
    entries=[]
    for category,items in [('masculino',MALE),('feminino',FEMALE),('barba',BEARDS)]:
        for ident,label,brief in items:
            entries.append({'id':ident,'label':label,'category':category,'brief':brief,'status':'pending'})
    return {'version':1,'existing_male':['curto_classico','medio_ondulado','crespo_curto'],'entries':entries}

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    path=root/'assets/source/hair-catalog-v1/production-plan.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(plan(),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(path)
