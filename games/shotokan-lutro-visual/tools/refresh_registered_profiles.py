"""Re-bake existing registered appearances after audited base sprite corrections."""
import json
from pathlib import Path
from compile_character import compile
HERE=Path(__file__).resolve().parents[1]
roster=json.loads((HERE/'assets/characters.json').read_text(encoding='utf8'));path=HERE/'assets/character-visuals.json';profiles=json.loads(path.read_text());original=json.dumps(profiles,sort_keys=True)
for s in roster['students'].values():
 if s.get('visual'):profiles[s['visual']]=compile(s,HERE/'src/assets')
if json.dumps(profiles,sort_keys=True)!=original:
 from character_registry import write
 write(path,profiles)
print('Registered visual profiles refreshed; names, IDs and preferences preserved')
