# Deshi Dojo — combate Shotokan, bases neutras 2D

Esta edição usa as **seis bases neutras 2D aprovadas**: criança, adolescente e adulto, masculinos e femininos, carecas e sem feições. Cada corpo tem 92 quadros básicos e 72 quadros de especiais, queda e finalização, totalizando 984 posições. A arte anterior foi substituída. [Fontes, revisão, demonstrações e validação desta edição](docs/avatar-set-v3/README.md).

O **criador de personagens** funciona no notebook: execute `python scripts/play_web.py` na raiz do repositório e abra `http://localhost:8000/editor`. Nome, corpo, faixa, pele, pequenas proporções e emblema continuam configuráveis sem editar Lua. As bases desta etapa permanecem sem rosto e cabelo; as antigas identidades foram retiradas. Rostos e cabelos novos serão preparados para estas bases. [Como cadastrar alunos e exportar](docs/CRIADOR-DE-PERSONAGENS.md).

Os seletores abaixo da luta e o menu F2 permitem escolher entre os seis corpos e oito faixas para cada jogador. A faixa tem máscara exclusiva de cintura, nó e pontas; sua cor é independente da dificuldade da CPU. A guarda neutra cobre cabeça e tronco; a defesa baixa cobre a linha baixa; uma troca de defesa mantém a cobertura anterior durante a preparação. As regras de combate foram preservadas.

Dois jogadores e três botões: **soco, defesa e chute**. A luta tem energia, 60 segundos e melhor de três rounds. **Treino livre** mantém energia e tempo para experimentar. O combate usa técnicas Shotokan e eventos de contato separados das regras de energia, permitindo futuramente pontuação por distância, linha e precisão.

A versão v04 corrige o atravessamento com uma barreira entre os corpos que preserva a ordem anterior ao movimento. Acelera os golpes básicos, guarda novas pressões durante recuperação/impacto e acrescenta reação ao receber golpe, recuo, combos por acertos consecutivos e uma apresentação mais simples. As animações são ilustrações provisórias: as que ainda não representam claramente a técnica foram retiradas dos comandos ativos, com fontes e catálogo preservados.
A versão v05 acrescenta **CPU offline**: fácil/faixa vermelha, médio/faixa laranja e difícil/faixa preta. O jogo inicia no fácil. Selecione **Contra a CPU** ou **2 jogadores** acima da luta; a CPU ocupa o jogador 2. Cada nível usa os mesmos golpes/regras, com diferença de observação, iniciativa, defesa e sequências. As faixas identificam o perfil no HUD/menu; o sprite provisório continua preservado. [Comportamento, arquitetura e testes da CPU](docs/CPU.md).

A v06 corrige a pressão repetida de soco e a prioridade da defesa: só ligações permitidas pulam a recuperação; iniciar outra sequência exige 16 ticks sem atacar, com movimento, defesa e salto disponíveis. Uma nova pressão de defesa remove um ataque antigo do buffer. A CPU prepara guarda durante o impacto, protege sua própria recuperação e reconhece sequências repetidas por observação atrasada. Energia, dano e sprites foram mantidos. [Diagnóstico, regras e regressões](docs/PRESSAO-E-DEFESA.md).

O IKEMEN e os dois projetos TIC-80 permanecem intactos. A amostra Lutro v01 inteira está preservada em `archives/shotokan-lutro-visual-v01.zip` na raiz do checkout, com manifesto SHA-256. Nenhum arquivo do fliperama foi acessado ou modificado.

## Jogar no notebook

Use o clone do repositório com Python 3.11+ e um navegador atual. Na raiz:

```bash
python scripts/play_web.py
```

No Linux/macOS, use `python3`; no Windows, `py -3` também funciona. O navegador abre em `http://localhost:8000`; deixe o terminal aberto durante a partida. Sem npm, Pillow, instalação do motor ou rede. Para atualizar o projeto, execute `git pull` na mesma pasta, em outro terminal, e pressione F5 no navegador. O servidor reconstrói o HTML ao detectar alterações no Lua, catálogo, template ou assets; não gera ZIPs. Ctrl+C encerra.

Porta ocupada: `python scripts/play_web.py --port 8001`. Para abrir o navegador manualmente: `python scripts/play_web.py --no-open`. O endereço é do servidor na sua própria máquina.

No Windows, `.gitattributes` preserva os bytes do interpretador Fengari. Clones antigos que já converteram esse arquivo para CRLF são reparados automaticamente pelo build, somente após confirmar o SHA-256 original dos bytes com LF. Alterações reais de conteúdo continuam sendo rejeitadas; não desative a checagem nem troque o hash para contornar erros.

O HTML em `dist/deshi-dojo-visual.html` também continua abrindo diretamente por arquivo. `python tools/build.py` gera HTML e cartucho. Os ZIPs antigos só são gerados ao acrescentar `--archives`; o fluxo de atualização continua pelo Git.

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

**Frente/trás são relativos ao adversário.** Cima sozinho salta; diagonal para cima salta com deslocamento. Baixo sozinho usa base baixa. Cima com um botão seleciona a técnica no chão, sem iniciar salto.

| Comando com soco/chute | Técnica |
|---|---|
| Primeiro soco sem direção | Kizami-zuki: mão dianteira |
| Segundo soco na sequência, sem direção | Gyaku-zuki: mão reversa |
| Trás + soco | Gyaku-zuki |
| Frente + soco | Gyaku-zuki com avanço curto, yori-ashi |
| Cima + soco | Gyaku-zuki jodan |
| Baixo + soco | Gyaku-zuki em base baixa |
| Chute sem direção | Mae-geri chudan |
| Frente + chute | Mawashi-geri chudan |
| Baixo + chute | Mae-geri gedan, estudo da linha baixa |
| No ar + soco | Tsuki durante o salto, adaptação de jogo |
| No ar + chute | Tobi-mae-geri |

Comece aproximando os dois jogadores e pressionando **soco → soco → chute**, soltando entre as pressões. O segundo soco seleciona automaticamente gyaku depois do kizami; o chute fecha com mae. Aperte durante o recolhimento ou um pouco antes: a nova pressão fica guardada por até 24 ticks e só executa quando o movimento anterior chega ao ponto permitido de retorno. Não é necessário acertar uma janela de apenas poucos quadros. Até três técnicas ligadas; depois há uma curta recomposição. Manter soco/chute não repete. O indicador **COMBO** conta contatos consecutivos enquanto o adversário ainda se recompõe; técnicas executadas que erram não aumentam esse contador.

Cima sozinho salta; diagonal para cima desloca o salto; baixo usa uma base baixa com os pés apoiados. Um ataque por salto, sem defesa aérea, salto duplo ou lançamento do adversário. O pouso recompõe por dois ticks. Os corpos também se bloqueiam durante o salto. Trás/cima + chute usam o frontal por enquanto; yoko, ushiro e mawashi alto/aéreo estão guardados fora dos comandos ativos até revisão. O antigo oi também está preservado: a animação de soco reverso com avanço recebe o nome gyaku com yori-ashi para corresponder ao movimento representado.

**Segure defesa.** Uma nova pressão substitui o ataque anterior no buffer, sem cancelar a extensão de um golpe em curso. O indicador **GUARDA ALTA/MEDIA/BAIXA** ou **RECEBE** confirma cobertura; PREPARA e IMPACTO ainda não protegem. Defesa sem direção mantém cobertura média; as quatro direções selecionam os uke acima. A defesa tem preparação e cobre somente a altura efetiva do contato. Mudar direção reinicia a preparação; soltar libera o movimento. Uma recepção no tempo abre uma janela de contra-ataque. Segure defesa **antes** de inclinar para cima para executar age-uke sem saltar; a defesa também substitui a impulsão enquanto os pés ainda estão no chão.

**Lutar** inicia uma partida com o modo/adversário escolhido. Trocar modo/nível também reinicia; Enter/Start preserva essa escolha. **Lutar** usa energia e rounds; golpes bloqueados não retiram energia. **Treino livre** não limita tempo/energia. Enter reinicia, Escape pausa no browser. F2/Select abre a seleção pelo direcional: soco/chute/Start confirma, defesa cancela. O relógio pausa durante essa seleção. Os indicadores dos comandos acendem e o nome/fase da técnica aparecem abaixo da luta. Em gamepads padrão no browser: A soco, X defesa, B chute; direcional/analógico movimenta, Start reinicia. A API foi testada com entradas simuladas; controles físicos/GPIO continuam pendentes.

Abra **Aprender os golpes e ver todos os comandos** quando quiser estudar. Selecione a técnica e clique **Ver movimento**; use câmera lenta, pausa, quadro único ou colisões. **Lutar** retorna ao controle livre. Combate e demonstração usam o mesmo Lua. O painel explicativo é do browser; o cartucho mostra nome/fase. Combinações simultâneas ainda dependem do teclado. Consulte [FUNDAMENTOS.md](docs/FUNDAMENTOS.md) para princípios, fontes e revisão pendente.

## Núcleo histórico no notebook

No checkout completo com Python, Pillow, Tk e compilador/Make:

```bash
python3 research/lutro/prepare.py
python3 games/shotokan-lutro-visual/tools/play_notebook.py
```

O viewer usa os mesmos comandos; Enter reinicia e F2 escolhe CPU/nível/dois jogadores. A preparação inicial baixa/verifica fontes; depois funciona offline. Não precisa dele para jogar o HTML. `.lutro` usa RETROPAD B = soco, Y = defesa, A = chute; direções dos dois ports. O mapeamento físico/GPIO no gabinete ainda precisa ser testado. Não copie bibliotecas x86 ao Pi.

## Fonte e reconstrução

`dist/deshi-dojo-visual.zip` inclui código/arte/ferramentas/documentação, além do HTML e cartucho. `src/main.lua` é a mesma lógica nos dois runtimes. `assets/techniques.json` define as técnicas; `tools/build.py` gera `src/techniques.lua`. `tools/import_art.py` importa sete folhas para células de 224×144 e atlases espelhados de 896×3312; extrai cada figura conectada na folha inteira, mesmo quando um membro atravessa a grade, gerando `src/art.lua` com limites visuais para as regiões vulneráveis. PNGs têm transparência binária para o blitter antigo; não há shaders, serviços externos ou recursos modernos do LÖVE.

```bash
python3 games/shotokan-lutro-visual/tools/import_art.py
python3 games/shotokan-lutro-visual/tools/build.py
python3 games/shotokan-lutro-visual/tests/native.py
python3 games/shotokan-lutro-visual/tests/cpu_native.py
python3 games/shotokan-lutro-visual/tests/pressure.py
node games/shotokan-lutro-visual/tests/cpu_browser.cjs
python3 games/shotokan-lutro-visual/tests/windows_checkout.py
node games/shotokan-lutro-visual/tests/browser.cjs
python3 games/shotokan-lutro-visual/tests/raster.py
python3 games/shotokan-lutro-visual/tools/capture.py
```

Execute da raiz do checkout. Import/build também funcionam no ZIP de fonte extraído, usando `python3 tools/import_art.py` e `python3 tools/build.py`; Pillow é ferramenta de autoria. Testes nativos requerem o checkout completo/núcleo preparado; browser requer Playwright/Chromium, apenas no desenvolvimento. O jogo HTML não requer nenhuma dessas dependências.

Sem monitor no ambiente cloud:

```bash
PATH="$PWD/.cache/cloud-tools/usr/bin:$PATH" xvfb-run -a python3 games/shotokan-lutro-visual/tools/play_notebook.py --frames 120
```

## Evidências e pendências

O cartucho foi exercitado no núcleo histórico que a configuração oficial do Recalbox 6.1 fixa, compilado para Linux x86-64. Passaram 19 grupos nativos, 56 casos técnica/porta/orientação, 40 pares no chão, 10 no ar, quatro combos básicos com **três contatos reais**, 680 verificações de colisão por tick e 12 grupos no browser offline. Os testes adicionais da CPU verificam três partidas completas, sete grupos nativos e cinco no browser, incluindo 1.080 ticks de replay entre os interpretadores. São 92 cenas/poses/bordas comparadas pixel a pixel, incluindo reações, base baixa, perfis CPU e menu; espelhamento de 92 poses importadas verificado. **Isso não comprova desempenho/compatibilidade ARM ou GPIO no Raspberry Pi 3, nem certifica a biomecânica das poses.** Leia [COMPATIBILIDADE.md](docs/COMPATIBILIDADE.md) e os resultados JSON.
Para um futuro teste no gabinete: verificar alimentação/baixa tensão, obter acesso ao cartão, fazer backup verificável, identificar o núcleo/diretório realmente instalados e adicionar apenas o cartucho novo. Não atualizar Recalbox, sobrescrever jogos/configurações ou alterar GPIO. Ainda medir desempenho, memória total, temperatura, latência/monitor, duas portas físicas e saída/reabertura.

[Captura das técnicas no jogo](docs/fundamentos.gif) · [age-uke](docs/age-3x.png) · [gedan-barai](docs/gedan-3x.png) · [soto-uke](docs/soto-3x.png) · [uchi-uke](docs/uchi-3x.png) · [mawashi](docs/mawashi-3x.png).

A extração usada desde v03 corrige o pé do mawashi: a folha original atravessava a divisória entre os quadros 35 e 36. A extração por figura preserva o pé no quadro 35 e remove o fragmento do 36. Os testes verificam as duas orientações e recorte nas bordas, sem alterar a folha original.

Para age-uke, segure defesa e depois incline para cima. Defesa também substitui a impulsão enquanto os pés ainda estão no chão; após sair do chão não há bloqueio aéreo.
