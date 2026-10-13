"""Withdraw art from selection without destroying assets or stored presets."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from character_registry import read,catalog,validate
from hair_art import styles,beards
config=read(ROOT/'assets/characters.json');manifest=read(ROOT/'assets/character-assets.json')
offer=catalog(config,manifest)
approved={'default','masculino_curto','feminino_chanel'}
assert {e['id'] for e in offer['hair_styles']}==approved
assert [e['id'] for e in offer['beard_styles']]==['default']
assert all(set(body['hair'])==approved for body in offer['parts'].values())
assert len(styles())==25 and len(beards())==6,'Authored sources must survive withdrawal'
student={**next(iter(config['students'].values())),'hair':'buzz_uniforme','beard':'barba_cheia'}
validate(student,config,manifest)
stored={**config,'students':{**config['students'],'legacy':student}}
offer=catalog(stored,manifest)
assert any(e['id']=='buzz_uniforme' for e in offer['hair_styles'])
assert any(e['id']=='barba_cheia' for e in offer['beard_styles'])
assert all('buzz_uniforme' in body['hair'] for body in offer['parts'].values())
print('PASS only two approved cuts offered; rejected sources and stored configurations preserved')
