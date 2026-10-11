# Deshi Dojo — fundamentos Shotokan, Lutro v02

Dois jogadores, **três botões de ação**, quatro defesas direcionais, socos e chutes com preparação/contato/recolhimento. São 44 poses originais de um karateca fictício com cerca de 128 px de altura em uma cena de 384×224. Há acertos controlados, defesa por altura e janela de contra-ataque; sem HP. As regras são experimentais, não arbitragem oficial.

O IKEMEN e os dois projetos TIC-80 permanecem intactos. A amostra Lutro v01 inteira está preservada em `archives/shotokan-lutro-visual-v01.zip` na raiz do checkout, com manifesto SHA-256. Nenhum arquivo do fliperama foi acessado ou modificado.

## Jogar no notebook

Use o clone do repositório com Python 3.11+ e um navegador atual. Na raiz:

```bash
python scripts/play_web.py
```

No Linux/macOS, use `python3`; no Windows, `py -3` também funciona. O navegador abre em `http://localhost:8000`; deixe o terminal aberto durante a partida. Sem npm, Pillow, instalação do motor ou rede. Para atualizar o projeto, execute `git pull` na mesma pasta, em outro terminal, e pressione F5 no navegador. O servidor reconstrói o HTML ao detectar alterações no Lua, catálogo, template ou assets; não gera ZIPs. Ctrl+C encerra.

Porta ocupada: `python scripts/play_web.py --port 8001`. Para abrir o navegador manualmente: `python scripts/play_web.py --no-open`. O endereço é do servidor na sua própria máquina.

O HTML em `dist/deshi-dojo-visual.html` também continua abrindo diretamente por arquivo. ZIPs são uma opção de distribuição gerada por `tools/build.py`, não o fluxo necessário para desenvolver ou jogar pelo Git.

| Controle | Jogador 1 | Jogador 2 |
|---|---|---|
| Direções | Setas ↑ ↓ ← → | I cima, K baixo, J esquerda, L direita |
| Soco | Z | F |
| Defesa | X | G |
| Chute | A | H |

| Direção junto da defesa | Técnica |
|---|---|
| Cima | Age-uke — linha alta |
| Baixo | Gedan-barai — linha baixa |
| Frente | Soto-uke — linha média |
| Trás | Uchi-uke — linha média |

**Frente/trás são relativos ao adversário.** Sem direção: gyaku-zuki chūdan, guarda média e mae-geri chūdan. Soco + frente dá oi-zuki; + cima dá gyaku alto. Chute + frente dá mawashi-geri; + baixo dá mae baixo para kihon. Cima/baixo são modificadores, não salto/agachamento.

Aproxime-se e pressione novamente após o retorno; segurar soco/chute não repete. Defesa tem preparação e cobre somente sua linha. Segurando, mantém cobertura; trocar direção reinicia a preparação. Uma recepção no tempo abre uma janela de contra-ataque. **Ver colisões** mostra três alturas e o punho/pé ativos. **Recomeçar** reinicia posições/acertos.

Para estudar, selecione uma técnica e clique **Estudar técnica**. O painel explica suas fases; **Câmera lenta**, **Pausar** e **Um quadro** permitem observar. Clique **Jogar** para voltar ao controle livre. Limitações de combinações simultâneas dependem do teclado. O painel de estudo é do HTML; o cartucho mostra técnica/fase durante o combate. Poses e fundamentos precisam de revisão do instrutor do dojo: veja [FUNDAMENTOS.md](docs/FUNDAMENTOS.md).

## Núcleo histórico no notebook

No checkout completo com Python, Pillow, Tk e compilador/Make:

```bash
python3 research/lutro/prepare.py
python3 games/shotokan-lutro-visual/tools/play_notebook.py
```

O viewer usa os mesmos comandos; Enter reinicia. A preparação inicial baixa/verifica fontes; depois funciona offline. Não precisa dele para jogar o HTML. `.lutro` usa RETROPAD B = soco, Y = defesa, A = chute; direções dos dois ports. O mapeamento físico/GPIO no gabinete ainda precisa ser testado. Não copie bibliotecas x86 ao Pi.

## Fonte e reconstrução

`dist/deshi-dojo-visual.zip` inclui código/arte/ferramentas/documentação, além do HTML e cartucho. `src/main.lua` é a mesma lógica nos dois runtimes. `assets/techniques.json` define as técnicas; `tools/build.py` gera `src/techniques.lua`. `tools/import_art.py` importa quatro folhas para células de 224×144 e atlases espelhados de 896×1584, gerando `src/art.lua`. PNGs têm transparência binária para o blitter antigo; não há shaders, serviços externos ou recursos modernos do LÖVE.

```bash
python3 games/shotokan-lutro-visual/tools/import_art.py
python3 games/shotokan-lutro-visual/tools/build.py
python3 games/shotokan-lutro-visual/tests/native.py
node games/shotokan-lutro-visual/tests/browser.cjs
python3 games/shotokan-lutro-visual/tools/capture.py
```

Execute da raiz do checkout. Import/build também funcionam no ZIP de fonte extraído, usando `python3 tools/import_art.py` e `python3 tools/build.py`; Pillow é ferramenta de autoria. Testes nativos requerem o checkout completo/núcleo preparado; browser requer Playwright/Chromium, apenas no desenvolvimento. O jogo HTML não requer nenhuma dessas dependências.

Sem monitor no ambiente cloud:

```bash
PATH="$PWD/.cache/cloud-tools/usr/bin:$PATH" xvfb-run -a python3 games/shotokan-lutro-visual/tools/play_notebook.py --frames 120
```

## Evidências e pendências

O cartucho foi exercitado no núcleo histórico que a configuração oficial do Recalbox 6.1 fixa, compilado para Linux x86-64. Passaram 40 casos técnica/porta/orientação, 30 combinações de altura, timing, contra-ataque e controles offline no browser. **Isso não comprova desempenho/compatibilidade ARM ou GPIO no Raspberry Pi 3.** Leia [COMPATIBILIDADE.md](docs/COMPATIBILIDADE.md), resultados JSON e suas ressalvas.

Para um futuro teste no gabinete: verificar alimentação/baixa tensão, obter acesso ao cartão, fazer backup verificável, identificar o núcleo/diretório realmente instalados e adicionar apenas o cartucho novo. Não atualizar Recalbox, sobrescrever jogos/configurações ou alterar GPIO. Ainda medir desempenho, memória total, temperatura, latência/monitor, duas portas físicas e saída/reabertura.

[Movimento real das técnicas](docs/fundamentos.gif) · [age-uke](docs/age-3x.png) · [gedan-barai](docs/gedan-3x.png) · [soto-uke](docs/soto-3x.png) · [uchi-uke](docs/uchi-3x.png) · [mawashi](docs/mawashi-3x.png).
