"""Serve the current Shotokan prototype locally with automatic HTML rebuilds.

Python standard library only; works independently of the terminal's directory.
No downloads, native engine, Pillow, npm or archive generation required.
"""
import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import threading
from urllib.parse import urlsplit
import webbrowser
import json,os,shutil,tempfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'games' / 'shotokan-lutro-visual'
PAGE = 'deshi-dojo-visual.html'
sys.path.insert(0,str(GAME/'tools'))
from character_registry import read,write,validate,catalog
EDITOR_LOCK=threading.Lock()

def compiler_python():
    try:
        import PIL,numpy
        return sys.executable
    except ImportError:
        bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
        if bundled.is_file():return str(bundled)
        raise ValueError('Preparacao visual requer Pillow no notebook. Instale com python -m pip install Pillow. O jogo nao precisa dessa biblioteca.')

def prepare_visual(student):
    output=ROOT/'.runtime/character-previews';output.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',encoding='utf-8',delete=False) as f:
        json.dump(student,f,ensure_ascii=False);source=Path(f.name)
    try:
        result=subprocess.run([compiler_python(),str(GAME/'tools/compile_character.py'),'--input',str(source),'--out',str(output)],capture_output=True,text=True,encoding='utf-8',timeout=90)
        if result.returncode:raise ValueError(result.stderr.strip() or 'Falha na preparacao visual.')
        return json.loads(result.stdout),output
    finally:source.unlink(missing_ok=True)

def save_student(student,builder):
    config_path=GAME/'assets/characters.json';visual_path=GAME/'assets/character-visuals.json'
    config=read(config_path);student=validate(student,config,read(GAME/'assets/character-assets.json'))
    visual,output=prepare_visual(student);profiles=read(visual_path) if visual_path.exists() else {}
    student['visual']=visual['id'];student['portrait']=visual['portrait']
    names=[visual['portrait']]
    names.extend(visual['parts']['body'][s] for s in ('right','left'))
    names.extend(p[s] for p in visual['parts']['belt'].values() for s in ('right','left'))
    for name in names:shutil.copyfile(output/(name+'.png'),GAME/'src/assets'/(name+'.png'))
    profiles[visual['id']]={k:v for k,v in visual.items() if k!='signature'}
    old_config=config_path.read_bytes();old_visual=visual_path.read_bytes() if visual_path.exists() else None
    config['students'][student['id']]=student
    config['student_order']=list(config['students'])
    try:
        write(visual_path,profiles);write(config_path,config)
        built=subprocess.run([sys.executable,str(GAME/'tools/build.py')],capture_output=True,timeout=60)
        if built.returncode:raise ValueError(built.stderr.decode('utf-8',errors='replace').strip() or 'Falha ao construir o jogo.')
        builder.signature=None
    except Exception:
        config_path.write_bytes(old_config)
        if old_visual is None:visual_path.unlink(missing_ok=True)
        else:visual_path.write_bytes(old_visual)
        raise
    return student


class Builder:
    def __init__(self):
        self.signature = None
        self.lock = threading.Lock()

    def refresh(self):
        paths = [
            GAME / 'src/main.lua', GAME / 'src/art.lua', GAME / 'src/cpu.lua',
            GAME / 'assets/techniques.json', GAME / 'assets/import.json',
            GAME / 'browser/template.html', GAME / 'browser/fengari-web.js',
            GAME / 'browser/runtime-provenance.json',
        ]
        paths += sorted(p for p in (GAME / 'src').glob('*.lua')
                        if p.name not in ('techniques.lua', 'character_data.lua'))
        paths += [GAME / 'tools/build.py', GAME / 'assets/characters.json', GAME / 'assets/character-assets.json', GAME / 'assets/specials.json', GAME / 'assets/special-assets.json', GAME / 'assets/ceremony.json', GAME / 'assets/ceremony-assets.json', GAME / 'assets/hand-touch-assets.json']
        paths += [p for p in (GAME/'tools/identity_art.py',GAME/'assets/character-identities.json',GAME/'assets/identity-adult-attachments.json') if p.exists()]
        paths += sorted((GAME/'assets/source/identities').glob('*.png'))
        paths += [p for p in (GAME/'tools/hair_art.py',GAME/'tools/hair_palette.py',GAME/'assets/hair-assets.json',GAME/'assets/hair-bindings.json') if p.exists()]
        paths += sorted((GAME/'assets/source/hair-v1').glob('*.png'))
        paths += [p for p in [GAME/'assets/character-visuals.json',GAME/'browser/editor.html',GAME/'tools/skin_palette.py',GAME/'tools/compile_character.py',GAME/'tools/character_registry.py',GAME/'tools/compile_special_profiles.py'] if p.exists()]
        paths += sorted(p for p in (GAME / 'src/assets').glob('*.png')
                        if not p.name.startswith('pose-'))
        with self.lock:
            signature = [(str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in paths]
            if signature != self.signature or not (GAME / 'dist' / PAGE).is_file():
                subprocess.run([sys.executable, str(GAME / 'tools/build.py'), '--web-only'],
                               cwd=ROOT, check=True, timeout=30)
                # The build refreshes derived visual metadata. Snapshot after
                # it completes so its own output does not trigger another build.
                self.signature = [(str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in paths]


def handler_for(builder):
    class Handler(SimpleHTTPRequestHandler):
        def json_response(self,status,value):
            data=json.dumps(value,ensure_ascii=False).encode('utf-8');self.send_response(status)
            self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)

        def do_POST(self):
            # Writes are loopback-only; reject browser requests from other origins.
            expected='http://'+self.headers.get('Host','')
            host=urlsplit(expected).hostname
            if host not in ('localhost','127.0.0.1','::1'):
                self.json_response(403,{'error':'Servidor de edicao restrito ao notebook local.'});return
            if self.headers.get('Origin',expected)!=expected or self.headers.get('Sec-Fetch-Site')=='cross-site':
                self.json_response(403,{'error':'Use o editor no mesmo servidor local.'});return
            if urlsplit(self.path).path not in ('/api/preview','/api/characters','/api/export'):
                self.json_response(404,{'error':'Endpoint inexistente.'});return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=16384:raise ValueError('JSON ausente ou muito grande.')
                value=json.loads(self.rfile.read(length))
                with EDITOR_LOCK:
                    route=urlsplit(self.path).path
                    if route=='/api/export':
                        subprocess.run([sys.executable,str(GAME/'tools/build.py')],check=True,capture_output=True,timeout=60)
                        self.json_response(200,{'html':'/'+PAGE,'cart':'/deshi-dojo-visual.lutro'});return
                    config=read(GAME/'assets/characters.json');student=validate(value,config,read(GAME/'assets/character-assets.json'))
                    if route=='/api/characters':
                        operation=self.headers.get('X-Character-Operation','upsert')
                        exists=student['id'] in config['students']
                        if operation=='create' and exists:raise ValueError('Este identificador ja existe. Edite o personagem salvo ou escolha outro ID.')
                        if operation=='update' and not exists:raise ValueError('Personagem nao encontrado para edicao.')
                        self.json_response(200,{'student':save_student(student,builder)});return
                    visual,_=prepare_visual(student);self.json_response(200,{'student':student,'visual':visual,'asset_base':'/preview-assets/'});return
            except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:self.json_response(400,{'error':str(e)})
            except (OSError,subprocess.SubprocessError) as e:self.json_response(500,{'error':'Falha ao gerar os recursos: '+str(e)})

        def end_headers(self):
            self.send_header('Cache-Control', 'no-store')
            super().end_headers()

        def prepare(self):
            path = urlsplit(self.path).path
            if path == '/favicon.ico':
                self.send_response(204)
                self.end_headers()
                return False
            if path not in ('/', '/' + PAGE):
                self.send_error(404)
                return False
            try:
                builder.refresh()
            except (OSError, subprocess.SubprocessError) as error:
                print('Falha ao reconstruir o jogo: ' + str(error), file=sys.stderr)
                self.send_error(500, 'Falha no build; veja o terminal.')
                return False
            query = urlsplit(self.path).query
            self.path = '/' + PAGE + ('?' + query if query else '')
            return True

        def do_GET(self):
            path=urlsplit(self.path).path
            if path=='/api/characters':
                config=read(GAME/'assets/characters.json');self.json_response(200,{'students':config['students'],'catalog':catalog(config,read(GAME/'assets/character-assets.json')),'techniques':read(GAME/'assets/techniques.json')});return
            if path=='/editor':
                data=(GAME/'browser/editor.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
            if path.startswith('/preview-assets/') or path.startswith('/portraits/'):
                name=path.rsplit('/',1)[-1]
                if not name.endswith('.png') or not all(c.isalnum() or c in '-_.' for c in name):self.send_error(404);return
                root=ROOT/'.runtime/character-previews' if path.startswith('/preview-assets/') else GAME/'src/assets'
                asset=root/name
                if not asset.is_file():self.send_error(404);return
                data=asset.read_bytes();self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
            if path=='/deshi-dojo-visual.lutro':
                data=(GAME/'dist/deshi-dojo-visual.lutro').read_bytes();self.send_response(200);self.send_header('Content-Type','application/zip');self.send_header('Content-Disposition','attachment; filename="deshi-dojo-visual.lutro"');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
            if self.prepare():
                super().do_GET()

        def do_HEAD(self):
            if self.prepare():
                super().do_HEAD()

    return functools.partial(Handler, directory=str(GAME / 'dist'))


def main():
    parser = argparse.ArgumentParser(description='Jogar Shotokan no navegador local')
    parser.add_argument('--port', type=int, default=8000, help='Porta HTTP (padrão: 8000)')
    parser.add_argument('--no-open', action='store_true', help='Não abrir navegador automaticamente')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('A porta deve estar entre 1 e 65535.')
    builder = Builder()
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), handler_for(builder))
    except OSError as error:
        parser.exit(1, f'Não foi possível abrir a porta {args.port}: {error}\n'
                       'Tente outra porta: --port 8001\n')
    with server:
        try:
            builder.refresh()
        except (OSError, subprocess.SubprocessError) as error:
            parser.exit(1, f'Não foi possível construir o jogo: {error}\n')
        address = f'http://localhost:{args.port}'
        print(f'Deshi Dojo pronto em {address}', flush=True)
        print(f'Editor de personagens: {address}/editor',flush=True)
        print('Atualize a página (F5) após editar ou usar git pull. Ctrl+C encerra.', flush=True)
        if not args.no_open:
            webbrowser.open(address)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nServidor encerrado.')


if __name__ == '__main__':
    main()
