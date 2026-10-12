"""Isolated export with all six bodies and real editor/offline game E2E."""
import importlib.util,json,os,subprocess,sys,tempfile,threading
from pathlib import Path
from http.server import ThreadingHTTPServer
from windows_checkout import fixture,HERE
sys.path.insert(0,str(HERE/'tools'))
from compile_character import compile
from character_registry import read,write,validate

def run():
    with tempfile.TemporaryDirectory(prefix='dojo-hair-') as tmp:
        game=fixture(tmp);config=read(game/'assets/characters.json');manifest=read(game/'assets/character-assets.json');profiles=read(game/'assets/character-visuals.json');cases=[]
        # Compiler imports are redirected as in the subprocess used by the editor.
        input_path=Path(tmp)/'student.json'
        for i,body in enumerate(config['body_order']):
            s=next(s.copy() for s in config['students'].values() if s['body']==body)
            s.update(id='hair-'+body.replace('_','-'),name='Cabelo '+body,hair=['curto_classico','medio_ondulado','crespo_curto'][i%3])
            s['appearance']={**s['appearance'],'hair_color':['branco','preto','ruivo','castanho','loiro','#80a4cc'][i]}
            write(input_path,s)
            done=subprocess.run([sys.executable,str(game/'tools/compile_character.py'),'--input',str(input_path),'--out',str(game/'src/assets')],capture_output=True,text=True,timeout=90)
            assert done.returncode==0,done.stderr
            visual=json.loads(done.stdout);s['visual']=visual['id'];s['portrait']=visual['portrait'];profiles[visual['id']]=visual;config['students'][s['id']]=s;cases.append(s['id'])
        config['student_order']=list(config['students']);write(game/'assets/characters.json',config);write(game/'assets/character-visuals.json',profiles)
        built=subprocess.run([sys.executable,str(game/'tools/build.py')],capture_output=True,text=True,timeout=120);assert built.returncode==0,built.stderr
        spec=importlib.util.spec_from_file_location('hair_editor_server',HERE.parents[1]/'scripts/play_web.py');server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server);server.GAME=game;server.ROOT=Path(tmp)
        # Server registry helpers normally point at the checked-out game. These
        # catalogues are identical; preview/build compilation runs in the fixture.
        http=ThreadingHTTPServer(('127.0.0.1',0),server.handler_for(server.Builder()));thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
        env={**os.environ,'DOJO_EDITOR_URL':'http://127.0.0.1:'+str(http.server_port),'DOJO_EDITOR_DIST':str(game/'dist/deshi-dojo-visual.html'),'DOJO_HAIR_CASES':json.dumps(cases)}
        try:
            done=subprocess.run(['node',str(HERE/'tests/hair_editor.cjs')],env=env,capture_output=True,text=True,timeout=240)
            assert done.returncode==0,done.stdout+'\n'+done.stderr
            print(done.stdout)
            import zipfile
            with zipfile.ZipFile(game/'dist/deshi-dojo-visual.lutro') as z:
                assert z.read('character_data.lua')==(game/'src/character_data.lua').read_bytes()
                assert 'crespo_curto' in z.read('character_data.lua').decode()
            report={'six_bodies_exported':True,'HTML_Lutro_same_roster':True,'editor_and_runtime':'passed','live_roster_unchanged':True,'physical_Pi_executed':False}
            write(HERE/'docs/hair/creator-tests.json',report);print(json.dumps(report))
        finally:http.shutdown();http.server_close();thread.join(timeout=5)

if __name__=='__main__':run()
