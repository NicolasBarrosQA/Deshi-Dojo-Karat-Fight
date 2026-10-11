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

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'games' / 'shotokan-lutro-visual'
PAGE = 'deshi-dojo-visual.html'


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
        paths += sorted(p for p in (GAME / 'src/assets').glob('*.png')
                        if not p.name.startswith('pose-'))
        with self.lock:
            signature = [(str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in paths]
            if signature != self.signature or not (GAME / 'dist' / PAGE).is_file():
                subprocess.run([sys.executable, str(GAME / 'tools/build.py'), '--web-only'],
                               cwd=ROOT, check=True, timeout=30)
                self.signature = signature


def handler_for(builder):
    class Handler(SimpleHTTPRequestHandler):
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
        print('Atualize a página (F5) após editar ou usar git pull. Ctrl+C encerra.', flush=True)
        if not args.no_open:
            webbrowser.open(address)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nServidor encerrado.')


if __name__ == '__main__':
    main()
