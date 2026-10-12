# Reverência, yoi e kiba-dachi

O estado aprovado anterior foi publicado primeiro no GitHub, no commit `0f4e931`, branch `codex/shotokan-specials`.

Os seis corpos agora possuem uma folha original 2D de apresentação. A base baixa usa a pose de kiba-dachi: base simétrica, joelhos flexionados e os dois punhos recolhidos. O soco baixo continua sendo um ataque independente, com suas animações e regras anteriores. As bandas de colisão da base baixa foram preservadas.

Antes de cada round: atenção → reverência/OSS → retorno → yoi → entrada em kamae → HAJIME. São 300 ticks a 60 Hz. Durante esse período, energia, relógio do round, CPU, movimentos, golpes e histórico de comandos permanecem bloqueados. Botões apertados durante a saudação não deixam ataques ou saltos pendentes. O menu pausa a abertura; reiniciar começa uma abertura nova. Treino e demonstrações didáticas entram diretamente nos movimentos.

No HTML, a abertura usa tempo real, mesmo em câmera lenta. Os golpes continuam obedecendo à velocidade escolhida. A pose final reutiliza a guarda aprovada pixel por pixel, incluindo cada faixa. As novas poses mantêm escala craniana e contato dos pés com o tatame. Todas as faixas e paletas de pele usam a mesma compilação dos outros movimentos.

Arte: ferramenta integrada imagegen, seis gerações separadas com as bases aprovadas como referência. Fontes e conjunto integral de prompts: `assets/source/ceremony/`. Nenhum modelo 3D ou deformação de um sprite para inventar movimentos. A importação só extrai, ajusta a escala, ancora, separa a faixa e empacota os desenhos.

Risco de regressão: alto, porque a abertura bloqueia o início do combate. Validação executada:

- `tests/ceremony.cjs`: seis corpos, P1/P2, 300 ticks, tempo real em 0,25x, bloqueio da CPU/energia/relógio/buffer, botões segurados, próximo round, menu, treino, kiba e soco baixo. Também verifica alocações e re-seleção sob a API histórica de imagens.
- `tests/ceremony_assets.py`: 54 quadros, 432 combinações de faixa, 648 de pele, espelhamento, transparência, escala, piso e identidade exata da guarda final.
- `tests/browser.cjs`: 13 grupos de regressão, incluindo barreiras, comandos, defesas, combos, golpes, saltos, gamepad simulado e loop real.
- `tests/specials.cjs`: parser, rasteira/finalização, ambos os lados, bloqueio, expiração, especiais e CPU.
- `tests/jump_anchor.cjs`: 24 saltos reais, seis corpos e ambos os ports, continuidade da física e do desenho.
- `tests/playback.cjs`: velocidade didática e cadência real.
- `tests/character_creator.py`: editor CRUD/exportação, personalização, 81 quadros de especiais/apresentação com pele retinta, combate, CPU e cache.
- `tests/package.py`, `tests/editor_rebuild_cache.py`, compilação Python e `git diff --check`.

`adults.gif`, `teens.gif` e `children.gif` são quadros capturados do canvas real do HTML offline, sem interpolação ou animações simuladas. Os traces e hashes estão nesta pasta. Cada GIF mostra os cinco segundos da abertura e a base kiba-dachi depois de liberar o combate.

HTML offline e cartucho atualizados estão em `dist/`; integridade em `SHA256SUMS.txt`. As seis novas folhas, usando uma faixa por corpo, somam 3.486.184 bytes de imagens decodificadas, carregadas conforme os personagens selecionados no cartucho. O hardware físico Raspberry Pi 3/Recalbox não foi executado nesta validação; o teste de orçamento e API local não substitui esse teste físico.
