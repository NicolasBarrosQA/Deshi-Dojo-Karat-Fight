# Seis bases neutras 2D — movimentos completos

Esta edição substitui a arte anterior pelos seis corpos aprovados: criança, adolescente e adulto, masculinos e femininos. Cada corpo tem 92 quadros básicos e 72 de especiais/queda, totalizando 984 posições. Carecas, sem feições, karategi branco; a personalização de rosto e cabelo será feita sobre estas bases.

Toda a execução é 2D com PNGs e quads do Lutro histórico. Não há modelos, rig ou renderização 3D no jogo. A fonte artística está em `assets/source/avatar-set-v3`: 114 folhas originais, prompts completos em `jobs.json`, edições pontuais e `corrections.json`. As seis referências aprovadas permanecem em `assets/source/avatar-bases-v2` e `assets/source/avatar-poses-2d-v1`.

O importador faz extração por figura inteira, alpha binário e empacotamento compacto. A escala usa referências explícitas em pé e o diâmetro da parte superior da cabeça, excluindo a área variável de pescoço e peito. Cada quadro recebe escala uniforme na preparação; pernas dobradas não diminuem o restante do corpo. As seis guardas aprovadas permanecem idênticas. `scale-correction.json` e `tests/avatar_scale.py` registram a correção e sua regressão. A faixa é desenhada com marcador magenta apenas na fonte para extrair cintura, nó e duas pontas; os oito tons são preparados em arquivos separados. Nenhum marcador magenta é usado no jogo. Há uma oclusão revisada em que o joelho/gi cobre inteiramente a faixa; esse quadro não recebe cor sobre a perna.

Os quadros de guarda ao começar/terminar os especiais usam a própria guarda da nova base, para manter continuidade. Preparação, execução, contato e reação têm arte própria. Os quadros de solo recebem a direção apropriada da pose deitada desenhada, para continuar a queda para trás. O sprite em pé não é girado para representar uma queda.

A pose de descida do salto (63) mantém o mesmo centro horizontal de cabeça/tronco da subida (62). A correção muda somente a posição do quadro, com espelhamento normal para P2; pixels, escala, velocidade, trajetória e colisões permanecem iguais. `jump-anchor-correction.json` registra os ajustes por corpo, e `jump-anchor-tests.json` verifica 24 saltos reais, verticais e para frente, nos seis corpos e dois ports, usando as coordenadas efetivas de desenho.

Valores de dano, controles, buffer, combos, defesas, barreira, energia, rounds, CPU offline e máquinas de estados permanecem no motor existente. As sequências de Ashi-barai e finalização continuam exigindo dois comandos do atacante. O adversário caído não contra-ataca nessa sequência.

As pranchas `*-review.png` mostram as posições exatas dos atlases. Os GIFs `*-ashi-sequence.gif` são gerados exclusivamente de frames do jogo capturados por comandos de teclado nos dois ports; o arquivo `capture-traces.json` registra estados e SHA-256 do HTML. A apresentação dos GIFs usa ampliação nearest-neighbor e reprodução em 0,5×.

Validação de arquivos: `asset-tests.json`, com 984 posições, 7.872 combinações de faixa e 8.856 verificações de proporção, incluindo espelhamento, máscara, alpha e enquadramento. A revisão visual está em `visual-audit.json`. Os resultados de execução estão em `browser-tests.json` e `delivery-report.json`: seis bases nos dois ports, 12 sequências reais de rasteira/finalização/recuperação, controles, defesas, CPU, comandos especiais e empacotamento aprovados. A arte anterior foi removida após os testes; o backup está fora do projeto. As validações automatizadas não certificam a biomecânica para instrução presencial.

O orçamento considera buffers RGBA reais, inclusive as duas direções. A biblioteca inteira de seis corpos e todas as oito faixas ocupa cerca de 131 MiB decodificados e não é carregada inteira durante uma partida. O teste de cache verifica a dupla e os recursos efetivamente carregados contra o limite de imagens de 128 MiB do cartucho. **Raspberry Pi 3/Recalbox 6.1 físico ainda não foi executado nesta máquina**; o empacotamento/API histórica e o limite de recursos são verificados localmente.

Preparação para desenvolvimento (Python com Pillow/NumPy no notebook):

```text
python tools/avatar_set_import.py
python tools/normalize_avatar_guards.py
python tests/avatar_set.py --staged
python tools/install_avatar_set.py
python tools/build.py
```

`install_avatar_set.py` recusa fontes incompletas e cria uma cópia recuperável fora do projeto antes de substituir a arte. A limpeza dos arquivos anteriores é separada, após os testes, com caminhos restritos ao jogo e verificação de hashes. Os scripts antigos de importação dos personagens não são o fluxo desta edição.
