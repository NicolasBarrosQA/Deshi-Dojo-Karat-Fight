# Abertura com ordens e toque de mãos

Antes de cada round: **REI → TOQUEM AS MÃOS → YOI → HAJIME!!!**. Os personagens fazem reverência, aproximam-se, encostam os punhos de forma amistosa, recolhem os braços, voltam às posições iniciais, assumem yoi e entram na guarda aprovada. O letreiro substitui a contagem numérica. A abertura dura 420 ticks (sete segundos a 60 Hz), inclusive no HTML em câmera lenta.

Os seis corpos têm nove novas poses originais de saudação, com três alturas de mão para encontros entre idades, alturas e portes diferentes. As posições são calculadas pelos pontos de contato dos desenhos, sem deformar os sprites. As poses anteriores de reverência, yoi, guarda e kiba-dachi permanecem disponíveis. Soco baixo e base baixa continuam separados.

Durante a abertura, energia, relógio do round, CPU, colisões de combate e comandos ofensivos ficam bloqueados. As posições de apresentação são restauradas antes do combate. Botões segurados não deixam ataques ou saltos pendentes. O menu pausa a abertura; treino e demonstrações entram diretamente nos movimentos.

Arte criada com imagegen a partir das bases aprovadas. Fontes e prompts: `assets/source/ceremony/` e `assets/source/hand-touch/`. `corrections.json` identifica os dois quadros baixos substituídos por desenhos corrigidos. A importação extrai, normaliza escala, ancora os pés, separa materiais e empacota. Todas as poses usam as mesmas paletas de pele e faixas do editor, compiladas para HTML offline e Lutro.

Risco de regressão: alto, por bloquear o início do combate. Validação desta alteração:

- `tests/ceremony.cjs`: seis corpos nos dois ports, 36 encontros entre corpos, contato efetivo, 420 ticks, tempo real em 0,25x, CPU/energia/relógio/buffer, botões segurados, próximo round, menu, treino, kiba e soco baixo; orçamento de imagens e re-seleção sem novas alocações.
- `tests/hand_touch_assets.py`: 54 poses, 432 faixas, 648 tons de pele e 2.916 encontros entre corpo/altura/porte; transparência, espelhamento, piso e materiais.
- `tests/ceremony_assets.py`: poses anteriores, faixas, pele e identidade exata da guarda final.
- `tests/browser.cjs`: 13 grupos de regressão de movimento, barreiras, defesas, combos, golpes, saltos, gamepad simulado e loop real.
- `tests/specials.cjs`: comandos, rasteira/finalização deliberada, ambos os lados, bloqueio, expiração, especiais e CPU.
- `tests/character_creator.py`: CRUD, exportação, editor no navegador, personalização de 90 quadros de especiais/apresentação, combate e CPU.
- `tests/package.py`, `tests/editor_rebuild_cache.py`, compilação Python e `git diff --check`.

`adults.gif`, `teens.gif` e `children.gif` contêm capturas do canvas real do HTML offline, sem interpolação ou animação simulada. A codificação verifica cada quadro decodificado contra a captura correspondente. Traces, hashes e relatório estão nesta pasta. `runtime-review.png` reúne momentos reais da abertura e da base baixa.

Entregáveis atualizados em `dist/`, com hashes em `SHA256SUMS.txt`. A API histórica e o orçamento de imagens são verificados localmente; Raspberry Pi 3/Recalbox e joysticks físicos não foram executados nesta validação.
