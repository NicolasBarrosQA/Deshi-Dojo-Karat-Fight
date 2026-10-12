"""Local gallery of actual sprite review pages and traced gameplay GIFs."""
from pathlib import Path
import html,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/avatar-set-v3'
groups=[f'base-{i+1:02d}' for i in range(0,92,9)]+['ashi_barai','ashi_finish','knockdown','ura_mawashi','ushiro','tai_sabaki','renzoku','nidan']
parts=['<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Deshi Dojo — seis bases 2D</title><style>body{font:17px system-ui;margin:24px;background:#202733;color:#f0f2f5}a{color:#9dd7ff}img{max-width:100%;image-rendering:pixelated}section{margin:32px 0;padding:18px;background:#303b4b;border-radius:12px}h1{font-size:28px}p{max-width:950px}</style><h1>Seis bases neutras 2D — movimentos completos</h1><p>Criança, adolescente e adulto, masculinos e femininos, carecas e sem feições. 92 posições básicas e 72 de especiais/queda por corpo: 984 posições. Os GIFs abaixo vêm da execução real do HTML offline. As pranchas são revisões estáticas dos mesmos recursos desenhados no jogo.</p><p><a href="../../dist/deshi-dojo-visual.html">Abrir jogo offline</a> · <a href="../../dist/deshi-dojo-visual.lutro">Cartucho Lutro</a> · <a href="README.md">Relatório e testes</a></p>']
for gif in sorted((ROOT/'docs/special-captures').glob('scale-*.gif')):
    name=html.escape(gif.name);parts.append(f'<section><h2>Escala: {name}</h2><p>Guarda, soco, chute, salto, soco aéreo e aterrissagem. Captura real do jogo atualizado.</p><img loading="lazy" src="../special-captures/{name}" alt="Escala corrigida durante os movimentos"></section>')
for gif in sorted(OUT.glob('*-ashi-sequence.gif')):
    name=html.escape(gif.name);parts.append(f'<section><h2>{name}</h2><img loading="lazy" src="{name}" alt="Sequência real de rasteira, finalização e recuperação"></section>')
for gif in sorted((ROOT/'docs/special-captures').glob('*.gif')):
    if gif.name.startswith('scale-'):continue
    name=html.escape(gif.name);parts.append(f'<section><h2>{name}</h2><img loading="lazy" src="../special-captures/{name}" alt="Especial capturado na execução real do jogo"></section>')
for group in groups:
    parts.append(f'<section><h2>{group}</h2><a href="{group}-review.png"><img loading="lazy" src="{group}-review.png" alt="Todas as poses do grupo {group}, nos seis corpos"></a></section>')
parts.append('</html>');(OUT/'index.html').write_text('\n'.join(parts),encoding='utf8')
print('Updated local gallery of 19 review plates and available real-game GIFs.')
