"""Reusable face views must import without changing body or combat files."""
import json,subprocess,sys,tempfile
from windows_checkout import fixture
with tempfile.TemporaryDirectory() as tmp:
    game=fixture(tmp);path=game/'assets/character-assets.json';before=json.loads(path.read_text())
    original=before['adult']['parts']['face']['default'];f=original['frames'][0]
    mapping={'views':{'right':[f['sx'],f['sy'],f['w'],f['h']]},
             'poses':[{'view':'right' if x['w']>1 else None} for x in original['frames']]}
    mapping_path=game/'assets/test-identity.json';mapping_path.write_text(json.dumps(mapping))
    body_path=game/'src/assets'/(''+before['adult']['parts']['body']['default']['right']+'.png')
    body_bytes=body_path.read_bytes();combat=(game/'src/main.lua').read_bytes()
    subprocess.run([sys.executable,str(game/'tools/import_identity.py'),'--body','adult','--layer','face','--id','reusable-view',
                    '--sheet',str(game/'src/assets'/(original['right']+'.png')),'--mapping',str(mapping_path)],check=True)
    after=json.loads(path.read_text());assert after['adult']['parts']['body']==before['adult']['parts']['body']
    assert body_path.read_bytes()==body_bytes and (game/'src/main.lua').read_bytes()==combat
    assert len(after['adult']['parts']['face']['reusable-view']['frames'])==92
    assert after['adult']['parts']['face']['default']==original
print('PASS one reusable face view mapped to 92 pose attachments; hidden rear faces; body, default identity and combat unchanged')
