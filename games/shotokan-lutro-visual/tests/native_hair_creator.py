"""Export both approved cuts on all six bases without touching the real roster."""
import hashlib,importlib.util,json,os,subprocess,sys,tempfile,threading,zipfile
from pathlib import Path
from http.server import ThreadingHTTPServer
from windows_checkout import fixture,HERE
sys.path.insert(0,str(HERE/'tools'))
from character_registry import read,write

def main():
    roster=HERE/'assets/characters.json';before=hashlib.sha256(roster.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='dojo-native-hair-') as tmp:
        game=fixture(tmp);config=read(game/'assets/characters.json');profiles=read(game/'assets/character-visuals.json');cases=[]
        input_path=Path(tmp)/'student.json'
        for body in config['body_order']:
            for style,color in [('masculino_curto','castanho_escuro'),('feminino_chanel','branco')]:
                s=next(s.copy() for s in config['students'].values() if s['body']==body)
                s.update(id='native-'+body.replace('_','-')+'-'+('short' if style=='masculino_curto' else 'bob'),name='Teste '+body,hair=style,beard='default')
                s['appearance']={**s['appearance'],'hair_color':color};s.pop('visual',None);s.pop('portrait',None);write(input_path,s)
                done=subprocess.run([sys.executable,str(game/'tools/compile_character.py'),'--input',str(input_path),'--out',str(game/'src/assets')],capture_output=True,text=True,timeout=90)
                assert done.returncode==0,done.stderr
                v=json.loads(done.stdout);s['visual']=v['id'];s['portrait']=v['portrait'];profiles[v['id']]=v;config['students'][s['id']]=s;cases.append(s['id'])
        write(game/'assets/characters.json',config);write(game/'assets/character-visuals.json',profiles)
        built=subprocess.run([sys.executable,str(game/'tools/build.py')],capture_output=True,text=True,timeout=180);assert built.returncode==0,built.stdout+'\n'+built.stderr
        specials=read(game/'assets/special-profiles.json');footprints=[]
        for style_index in (0,1):
            surfaces={}
            for ident in cases[style_index::2]:
                student=config['students'][ident];profile=profiles[student['visual']]
                surfaces[profile['portrait']]=profile['portrait_bytes']
                parts=[profile['parts']['body'],profile['parts']['belt'][student['belt']]]
                for animation in specials[student['visual']]['groups'].values():parts.extend([animation['body'],animation['belts'][student['belt']]])
                for part in parts:
                    for side in ('right','left'):surfaces[part[side]]=part['decoded_bytes']//2
            total=sum(surfaces.values());assert total<128*1024*1024,('Full six-character roster exceeds native surface budget',style_index,total)
            footprints.append(total)
        write(HERE/'docs/hair-rebuild-v2/native-full-roster-budget.json',{'six_characters_per_roster':True,'both_facings_all_basic_special_greeting_poses':True,'decoded_surface_bytes':footprints,'budget_bytes':128*1024*1024,'physical_Pi_executed':False})
        with zipfile.ZipFile(game/'dist/deshi-dojo-visual.lutro') as z:
            assert z.read('character_data.lua')==(game/'src/character_data.lua').read_bytes()
            assert 'masculino_curto' in z.read('character_data.lua').decode()
        spec=importlib.util.spec_from_file_location('native_server',HERE.parents[1]/'scripts/play_web.py');server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server);server.GAME=game;server.ROOT=Path(tmp)
        http=ThreadingHTTPServer(('127.0.0.1',0),server.handler_for(server.Builder()));thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
        env={**os.environ,'DOJO_EDITOR_URL':'http://127.0.0.1:'+str(http.server_port),'DOJO_EDITOR_DIST':str(game/'dist/deshi-dojo-visual.html'),'DOJO_HAIR_CASES':json.dumps(cases)}
        try:
            done=subprocess.run(['node',str(HERE/'tests/native_hair_editor.cjs')],env=env,capture_output=True,text=True,timeout=420)
            assert done.returncode==0,done.stdout+'\n'+done.stderr
            print(done.stdout)
        finally:http.shutdown();http.server_close();thread.join(timeout=5)
    assert before==hashlib.sha256(roster.read_bytes()).hexdigest()
    print('PASS both cuts exported across six bodies; HTML/Lutro roster parity; live roster preserved')

if __name__=='__main__':main()
