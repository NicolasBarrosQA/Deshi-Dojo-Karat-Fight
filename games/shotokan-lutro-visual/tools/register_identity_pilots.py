"""Append fictional pilot characters without changing existing students."""
from pathlib import Path
from character_registry import read,write,DEFAULT,validate
from compile_character import compile
HERE=Path(__file__).resolve().parents[1]

def run():
    path=HERE/'assets/characters.json';config=read(path);manifest=read(HERE/'assets/character-assets.json')
    profiles_path=HERE/'assets/character-visuals.json';profiles=read(profiles_path)
    for identity,name in [('cacheada','Lia Piloto'),('franja','Caio Piloto'),('raspado','Renato Piloto'),('preso','Maya Piloto')]:
        key='pilot-adult-'+identity
        if key in config['students']:
            print('Preserved existing student:',key);continue
        student=validate({'id':key,'name':name,'nickname':'Personagem ficticio','body':'adult','belt':'preta','face':'default','hair':'default','identity':identity,'appearance':DEFAULT},config,manifest)
        profile=compile(student,HERE/'src/assets');student.update(visual=profile['id'],portrait=profile['portrait'])
        config['students'][key]=student;profiles[profile['id']]=profile
        print('Prepared',name,flush=True)
    config['student_order']=list(config['students']);write(profiles_path,profiles);write(path,config)

if __name__=='__main__':run()
