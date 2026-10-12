"""Prepare review-only 2D pose sheets; never changes the game assets.

Uses a single scale for the three poses of each body, anchored to floor 143.
Source paintings remain untouched. Output is a resolution study, not animation.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/source/avatar-poses-2d-v1'
OUT = ROOT / 'docs/avatar-poses-2d-v1'
BODIES = [('crianca-masculina', 93), ('crianca-feminina', 93),
          ('adolescente-masculino', 111), ('adolescente-feminina', 111),
          ('adulto-masculino', 129), ('adulta-feminina', 129)]
POSES = ['guarda', 'gyaku-zuki', 'mae-geri']

def extract_figures(sheet):
    """Connected row runs allow hands/feet to overlap column ranges safely."""
    mask = np.asarray(sheet.getchannel('A')) >= 128
    parents, runs, previous = [], [], []
    def root(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i
    for y, row in enumerate(mask):
        edges = np.flatnonzero(np.diff(np.pad(row.astype(np.int8), (1, 1))))
        current = []
        for start, end in zip(edges[::2], edges[1::2]):
            ident = len(parents)
            parents.append(ident)
            runs.append((y, int(start), int(end), ident))
            for ps, pe, pi in previous:
                if start <= pe and end >= ps:
                    parents[root(ident)] = root(pi)
            current.append((int(start), int(end), ident))
        previous = current
    groups = {}
    for y, start, end, ident in runs:
        groups.setdefault(root(ident), []).append((y, start, end))
    figures = sorted(groups.values(), key=lambda rs: sum(e-s for _, s, e in rs), reverse=True)[:3]
    if len(figures) != 3:
        raise ValueError('Expected three separate figures')
    figures.sort(key=lambda rs: min(s for _, s, _ in rs))
    result = []
    for rs in figures:
        left, right = min(s for _, s, _ in rs), max(e for _, _, e in rs)
        top, bottom = min(y for y, _, _ in rs), max(y for y, _, _ in rs)+1
        cropped = sheet.crop((left, top, right, bottom))
        keep = np.zeros((bottom-top, right-left), dtype=np.uint8)
        for y, start, end in rs:
            keep[y-top, start-left:end-left] = 255
        cropped.putalpha(Image.fromarray(keep))
        result.append(cropped)
    return result

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 24)
    contact = Image.new('RGB', (1500, 6 * 400), '#e6e8ee')
    native = Image.new('RGB', (1344, 6 * 360), '#e6e8ee')
    report = []
    for row, (name, height) in enumerate(BODIES):
        source = SOURCE / (name + '.png')
        sheet = Image.open(source).convert('RGBA')
        frames = extract_figures(sheet)
        scale = height / max(f.height for f in frames)
        body_out = OUT / name
        body_out.mkdir(exist_ok=True)
        ImageDraw.Draw(contact).text((16, row * 400 + 8), name, font=font, fill='#172033')
        ImageDraw.Draw(native).text((16, row * 360 + 8), name + ' — 224 × 144, ampliado 2×', font=font, fill='#172033')
        entries = []
        for col, frame in enumerate(frames):
            frame.save(body_out / (POSES[col] + '-fonte.png'))
            display = frame.copy()
            display.thumbnail((480, 330), Image.Resampling.LANCZOS)
            contact.paste(display, (col * 500 + (500-display.width)//2,
                                    row * 400 + 50 + 330-display.height), display)
            w, h = round(frame.width * scale), round(frame.height * scale)
            if w > 224 or h > 143:
                raise ValueError(f'Pose exceeds canvas: {name}/{col}, {w}x{h}')
            reduced = frame.resize((w, h), Image.Resampling.LANCZOS)
            reduced.putalpha(reduced.getchannel('A').point(lambda a: 255 if a >= 128 else 0))
            canvas = Image.new('RGBA', (224, 144))
            canvas.alpha_composite(reduced, ((224-w)//2, 143-h))
            canvas.save(body_out / (POSES[col] + '-224x144.png'))
            enlarged = canvas.resize((448, 288), Image.Resampling.NEAREST)
            native.paste(enlarged, (col*448, row*360+55), enlarged)
            entries.append({'pose': POSES[col], 'size': [w, h], 'ground': 143})
        report.append({'body': name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                       'source_size': list(sheet.size), 'uniform_scale': scale, 'poses': entries})
    contact.save(OUT / 'poses-2d-seis-corpos.png')
    native.save(OUT / 'estudo-resolucao-nativa.png')
    (OUT / 'manifest.json').write_text(json.dumps({'status': 'review_only_not_integrated',
        'native_canvas': [224, 144], 'runtime_frame_bytes': 224*144*4,
        'generation': 'built-in image_gen, original 2D illustrations', 'bodies': report},
        ensure_ascii=False, indent=2), encoding='utf-8')
    print('Prepared 18 pose crops and 18 native resolution samples. Game unchanged.')

if __name__ == '__main__':
    main()
