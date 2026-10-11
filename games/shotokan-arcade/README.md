# Deshi Dojo Karate Fight — Shotokan Arcade

Versão 02 com arte original, animações ampliadas, efeitos sonoros e combate por pontuação. Esta pasta evolui a base existente: o IKEMEN e `prototypes/tic80/` continuam preservados; a versão visual anterior completa está em `archives/shotokan-arcade-v01.zip` na raiz do repositório.

## Jogar agora no notebook

1. Extraia `dist/deshi-dojo-arcade.zip`.
2. Abra `deshi-dojo-arcade.html` em um navegador desktop com JavaScript habilitado.
3. Clique em **Escolher personagens**. Cada jogador escolhe com esquerda/direita e confirma com seu botão A. Ambos precisam confirmar.

O HTML contém o interpretador Lua, código e arte; não precisa de servidor, instalação, cadastro ou Internet. A versão browser usa o mesmo Lua e assets do `.tic`, com um adaptador Canvas. Não é o núcleo libretro nem um teste de desempenho do Pi. Não há suporte a controle USB no adaptador browser nesta etapa. Navegadores corporativos podem bloquear arquivos locais; nesse caso use o cartucho em um TIC-80 desktop ou o viewer Linux abaixo.

O ZIP também inclui o cartucho, `game.lua` com o código Lua completo, licenças, relatório/capturas em `docs/` e fontes de arte, áudio e testes em `source/`. A investigação do motor de resolução maior está em `docs/INVESTIGACAO-LUTRO.md`. Os caminhos `dist/`, `src/` e comandos de desenvolvimento abaixo referem-se ao repositório completo; no ZIP os arquivos jogáveis ficam diretamente na pasta extraída.

| Ação | Jogador 1 | Jogador 2 | TIC-80 |
|---|---|---|---|
| Direções | Setas | I / K / J / L | Cima / baixo / esquerda / direita |
| Oi-zuki / confirmar | Z | F | A |
| Gyaku-zuki / cancelar seleção | X | G | B |
| Mae-geri | A | R | X |
| Mawashi-geri | S | T | Y |
| Defender | Recuar | Recuar | Direção contrária ao adversário |
| Diagnóstico / voltar ao título | Z + X por 1 segundo | — | P1 A + B por 60 ticks |

Clique no jogo para focar o teclado. Só esquerda/direita movimentam no combate; cima/baixo são exibidos no diagnóstico. Não há salto/agachamento. Nas telas de resultado, esquerda/direita alternam **Revanche** e **Seleção**, e A confirma. O diagnóstico também tem botão próprio no HTML.

## O que há nesta versão

- REN e AKI: karategi branco, faixas e cabelos distintos, 33 poses por personagem, proporções diferentes, contornos, sombras, dobras, rotação do torso/faixa e pés descalços. Perfis de aparência em `src/characters.json` permitem refinar traços individuais sem alterar as regras. A seleção permite trocar os personagens e fazer confronto espelhado.
- Dojo com tatame em perspectiva, madeira, shoji, lanternas, bonsai e um painel ornamental original. O painel não pretende reproduzir uma caligrafia japonesa validada.
- Respiração em três poses, avanço com quatro quadros, recuo com transferência de peso, guarda, bloqueio, impacto, vitória/derrota e quatro técnicas com antecipação, intermediário, extensão e recolhimento específicos.
- Separação dos corpos, hurtboxes do torso por pose, defesa, uma colisão por execução, hitstop de 3 ticks no bloqueio/5 no contato, contra-ataques durante recuperação de erro e retorno gradual à distância após ponto. Um único comando recente pode entrar no buffer nos quatro últimos ticks da recuperação; manter um botão pressionado não encadeia golpes.
- Seleção independente, nomes/faixas, aviso PRONTOS/HAJIME, cronômetro de 60 segundos ativos, placar, vitória, empate e revanche. A introdução de 36 ticks pausa o tempo e ignora ataques; a tela de resultado tem 24 ticks de proteção contra confirmação acidental. Primeiro a atingir pelo menos 5 pontos vence; dois pontos podem ultrapassar o limite.
- Socos valem 1, chutes 2; contatos fora do alcance ou defendidos não pontuam. `G.judge(event, move)` permite trocar essa política sem reescrever animação/colisão. Distância e qualidade são aproximações em pixels, não avaliação oficial de kumite.

Há sete efeitos originais leves: passos espaçados, soco, chute, bloqueio, impacto, ponto e vitória. São 494 bytes de envelopes/formas de onda no cartucho, em quatro canais. No HTML o som começa após clique/tecla; o botão **Som** permite silenciar. O adaptador WebAudio usa os mesmos dados/acionamentos e aproxima a síntese histórica; não é emulação PCM idêntica. O viewer Tk de desenvolvimento descarta áudio; para ouvir use o HTML ou o TIC-80/RetroArch com saída de som configurada.

Não há música, IA, personagens reais ou modos/golpes adicionais. Mae-geri inclui elevação, extensão e recolhimento; mawashi-geri percorre uma trajetória curva projetada em 2D com mudanças de apoio/torso. A execução ainda precisa de revisão de um instrutor.

**Meta visual dos alunos:** TIC-80 conserva 240×136 e 16 cores. Esta versão melhora a animação e apresentação, mas não entrega ainda o detalhamento facial de sprites no nível desejado de Street Fighter. A investigação autorizada de resolução maior está em `research/lutro/README.md` na raiz do repositório; o jogo não foi migrado. PNGs atuais ampliados não substituem arte refinada em resolução nativa.

## Cartucho e execução nativa

O cartucho é `dist/shotokan-arcade.tic`. Em um TIC-80 desktop já instalado, carregue-o pelo comando `load shotokan-arcade.tic` no console, seguido de `run`, ou abra o arquivo pelo programa. Essa rota depende da versão/plataforma instalada e não foi testada em Windows/macOS. Configure os dois jogadores no programa; não presuma que ele usa as mesmas teclas do HTML.

Para o viewer Linux validado no ambiente de desenvolvimento, a partir da raiz do repositório:

```bash
# Preparação, precisa de Internet somente na primeira vez:
python3 prototypes/tic80/tools/build_runtime.py
# Depois da preparação, execução inteiramente offline (Python 3 + Tk):
python3 games/shotokan-arcade/tools/play_notebook.py
```

O viewer reutiliza o host libretro do protótipo original sem alterar seus arquivos. O `.so` preparado é x86-64 para desenvolvimento; não o copie ao Raspberry Pi.

## Desenvolvimento e verificação

`src/game.lua` contém combate e telas; `src/art.lua` contém os índices de poses. `assets/` contém sprites PNG, atlas e dados binários. `tools/draw_art.py` é a fonte autoral da arte. `dist/game.lua` reúne arte e jogo para o cartucho/browser.

Na raiz do repositório:

```bash
python3 games/shotokan-arcade/tools/build.py
.cache/tic80-legacy/lua53 games/shotokan-arcade/tests/combat.lua games/shotokan-arcade/dist/game.lua
python3 games/shotokan-arcade/tests/native_smoke.py
python3 games/shotokan-arcade/tests/audio_native.py
```

Os dois primeiros testes usam Python padrão e o runtime preparado; a prova de áudio grava WAV com Python padrão. São 28 testes de lógica, quatro grupos de integração histórica e sete efeitos verificados em PCM. Para regenerar arte e capturas, instale Pillow no ambiente de desenvolvimento e execute `tools/draw_art.py` e `tests/native_capture.py` desta pasta. A fonte bitmap MIT histórica está preservada em `assets/font.bin`. `tools/build_audio.py` regenera os efeitos originais, com Python padrão. As dependências de geração não entram no jogo.

Para regenerar o HTML: `python3 games/shotokan-arcade/tools/prepare_browser.py` verifica e prepara Fengari 0.1.4; depois `python3 games/shotokan-arcade/tools/build_browser.py` embute tudo e gera o ZIP. A primeira preparação exige rede, a compilação seguinte não. `tests/browser.cjs` usa Playwright e Chromium somente para desenvolvimento. O caminho de Chromium no teste corresponde ao ambiente cloud validado.

## Futuro teste no Recalbox, sem substituir jogos

Este trabalho não acessou nem alterou o fliperama. Antes de gravar no cartão, verificar a alimentação (houve avisos de baixa tensão), fazer backup verificável do microSD e identificar a versão realmente instalada do núcleo e o espaço disponível.

Com isso resolvido e acesso ao cartão/share disponível, adicionar somente uma cópia de `shotokan-arcade.tic` em `/recalbox/share/roms/tic80/`, pelo método de transferência suportado pelo equipamento. Atualizar a lista de jogos pelo EmulationStation e executar pelo núcleo TIC-80 existente. Não atualizar Recalbox, trocar drivers GPIO/núcleos nem substituir ROMs ou configurações.

Abrir primeiro o diagnóstico. Verificar separadamente direções e quatro ações dos dois joysticks, inclusive combinações simultâneas. No núcleo histórico, A/B/X/Y do TIC correspondem a **B/A/Y/X do RetroPad**; a posição física dos botões GPIO ainda é desconhecida. Conferir a hotkey existente de saída antes de uma partida. Depois medir fluidez, latência, temperatura e eventuais avisos de tensão por 10–15 minutos e conferir os jogos antigos. Os dois botões físicos adicionais não são exigidos pelo jogo.

## Evidências e limites

Veja [compatibilidade e avaliação visual](docs/COMPATIBILIDADE.md), a [captura de combate](docs/kumite-4x.png), [resultado](docs/result-4x.png) e a [sequência animada real dos quatro golpes](docs/kumite-execution.gif) e a [comparação v01/v02](docs/comparison.png). São frames do cartucho entregue no núcleo histórico compilado para x86-64, ampliados sem suavização; não imagens conceituais.

**ARM, desempenho no Pi 3, GPIO, notebook pessoal e instalação física continuam pendentes.** Arte/código originais sob MIT. O HTML inclui Fengari MIT e a fonte bitmap histórica TIC-80 MIT; os avisos acompanham o ZIP. Nenhum sprite de Street Fighter, KOF, MUGEN ou IKEMEN foi utilizado aqui.
