"""Isolated HTTP CRUD/build tests and real editor/game E2E; never edits live roster."""
import copy,importlib.util,json,os,shutil,subprocess,sys,tempfile,threading,urllib.request,urllib.error
from pathlib import Path
from http.server import ThreadingHTTPServer
from windows_checkout import fixture,HERE
sys.path.insert(0,str(HERE/'tools'))
from character_registry import validate,visual_key,catalog
from compile_character import compile,transform
from PIL import Image

def run():
    checks=[];config=json.loads((HERE/'assets/characters.json').read_text(encoding='utf-8'));manifest=json.loads((HERE/'assets/character-assets.json').read_text())
    original=validate({'id':'example',**config['students']['demo-child']},config,manifest)
    other={**original,'id':'other','name':'Outro exemplo','belt':'preta'}
    assert visual_key(original)==visual_key(other)
    checks.append('Appearance keys reuse animation/atlas across names, IDs and belts')
    for field,value in [('id','../private'),('body','ghost'),('belt','azul'),('face','missing'),('hair','missing'),('name','')]:
        try:validate({**original,field:value},config,manifest)
        except ValueError:pass
        else:raise AssertionError(field)
    for field,value in [('skin','missing'),('height',2),('build','missing'),('hair_color','missing')]:
        try:validate({**original,'appearance':{**original['appearance'],field:value}},config,manifest)
        except ValueError:pass
        else:raise AssertionError(field)
    checks.append('Configuration errors rejected with explicit messages')
    for body in config['body_order']:
        source=Image.open(HERE/'docs'/('character-'+body+'-atlas.png')) if (HERE/'docs'/('character-'+body+'-atlas.png')).exists() else None
        # Every authored pose must remain inside the logical cell for all presets.
        from compile_character import layer_frames
        frames=layer_frames(body,'body','default',manifest)
        for height in (.94,1,1.04):
            for build in ('leve','medio','forte'):
                for frame in frames:transform(frame,{'height':height,'build':build})
    checks.append('All 2484 body/pose/height/build transforms stay inside cells, anchored to the same floor')
    spec=importlib.util.spec_from_file_location('editor_server',HERE.parents[1]/'scripts/play_web.py');server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
    with tempfile.TemporaryDirectory(prefix='dojo-editor-') as tmp:
        game=fixture(tmp);shutil.copyfile(HERE/'assets/character-masks.json',game/'assets/character-masks.json')
        server.GAME=game;server.ROOT=Path(tmp)
        handler=server.handler_for(server.Builder());http=ThreadingHTTPServer(('127.0.0.1',0),handler)
        thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start();url='http://127.0.0.1:'+str(http.server_port)
        def request(route,data=None,headers=None):
            req=urllib.request.Request(url+route,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json',**(headers or {})})
            try:
                with urllib.request.urlopen(req,timeout=120) as response:return response.status,json.loads(response.read())
            except urllib.error.HTTPError as e:return e.code,json.loads(e.read())
        try:
            students=[]
            for i in range(9):
                base=config['students'][['demo-adult','demo-teen','demo-child'][i%3]]
                student={**base,'id':'test-'+str(i),'name':'Exemplo '+str(i)}
                if i==0:student['appearance']={**student.get('appearance',{}),'skin':'retinta'}
                status,result=request('/api/characters',student,{'X-Character-Operation':'create'});assert status==200,result;students.append(result['student'])
            assert len({s['visual'] for s in students})==4
            deep=json.loads((game/'assets/special-profiles.json').read_text())[students[0]['visual']]
            assert set(deep['groups'])=={'ashi_barai','ashi_finish','knockdown','ura_mawashi','ushiro','tai_sabaki','renzoku','nidan','ceremony'}
            assert all(len(group['body']['frames'])==9 for group in deep['groups'].values())
            from skin_palette import apply_skin_palette
            sources=json.loads((game/'assets/special-assets.json').read_text())['adult']
            sources['ceremony']=json.loads((game/'assets/ceremony-assets.json').read_text())['adult']
            def special_frame(part,index):
                f=part['frames'][index];atlas=Image.open(game/'src/assets'/(part['right']+'.png')).convert('RGBA');frame=Image.new('RGBA',(224,144));frame.paste(atlas.crop((f['sx'],f['sy'],f['sx']+f['w'],f['sy']+f['h'])),(f['x'],f['y']));return frame
            for group,record in deep['groups'].items():
                for index in range(9):assert special_frame(record['body'],index).tobytes()==apply_skin_palette(special_frame(sources[group]['body'],index),'retinta').tobytes(),(group,index,'Exported special skin differs from preview material')
            checks.append('Retinta is baked exactly into all 81 special/knockdown/presentation frames, using the same material as basic moves')
            status,result=request('/api/characters',students[0],{'X-Character-Operation':'create'});assert status==400 and 'identificador' in result['error']
            edited={**students[0],'name':'Exemplo editado','belt':'preta'}
            status,result=request('/api/characters',edited,{'X-Character-Operation':'update'});assert status==200,result;assert result['student']['visual']==students[0]['visual']
            status,result=request('/api/characters');assert status==200 and result['students']['test-0']['name']=='Exemplo editado'
            persisted=json.loads((game/'assets/characters.json').read_text(encoding='utf-8'));assert persisted['students']['test-0']['belt']=='preta'
            status,_=request('/api/characters',edited,{'Origin':'https://example.invalid'});assert status==403
            checks.append('9 characters across 3 bodies: create, edit, duplicate ID, persistence, shared profiles and same-origin write protection')
            env={**os.environ,'DOJO_EDITOR_URL':url,'DOJO_EDITOR_DIST':str(game/'dist/deshi-dojo-visual.html')}
            result=subprocess.run(['node',str(HERE/'tests/character_editor.cjs')],env=env,capture_output=True,text=True,timeout=180)
            if result.returncode:raise AssertionError(result.stdout+'\n'+result.stderr)
            print(result.stdout)
            checks.append('Real editor create -> personalize -> save -> reopen -> select P1/P2 -> keyboard combat -> CPU -> offline HTML')
            import zipfile
            with zipfile.ZipFile(game/'dist/deshi-dojo-visual.lutro') as z:
                assert z.read('character_data.lua')==(game/'src/character_data.lua').read_bytes()
                assert 'EDITOR QA' in z.read('character_data.lua').decode()
            checks.append('Generated Lutro contains the same validated roster and appearance manifests as HTML; physical Pi not executed')
        finally:http.shutdown();http.server_close();thread.join(timeout=5)
    output={'checks':checks,'native_core_executed':False,'raspberry_pi_executed':False}
    (HERE/'docs/character-creator-results.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(output,indent=2))
if __name__=='__main__':run()
