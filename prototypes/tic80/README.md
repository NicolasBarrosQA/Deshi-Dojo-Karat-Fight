# Deshi Dojo — protótipo TIC-80 para dois jogadores

[Cartucho pronto](dist/deshi-dojo.tic) · [Fonte Lua](src/dojo.lua) · [Compatibilidade e testes](docs/COMPATIBILIDADE.md)

Este protótipo é independente do IKEMEN. Nenhum arquivo do fliperama é alterado por seus scripts. O cartucho é autocontido e usa apenas código Lua, paleta e primitivas gráficas; não baixa recursos, não usa rede, não grava progresso e não precisa de BIOS. Sem música nesta primeira versão.

## Duas telas

1. **Diagnóstico:** movimento independente em quatro direções, indicadores U/D/L/R/A/B/X/Y de cada jogador.
2. **Kumite experimental:** dois lutadores provisórios, cenário, colisão dos corpos, limites de arena, defesa para trás e quatro ataques com preparação, fase ativa e recuperação.

| Ação TIC-80 | Função |
|---|---|
| A | Oi-zuki, com pequeno avanço |
| B | Gyaku-zuki |
| X | Mae-geri |
| Y | Mawashi-geri |
| P1 A+B por 1 segundo | Alternar diagnóstico/kumite; reinicia a luta |
| P1 X+Y por 1 segundo | Reiniciar |

As combinações usam somente os quatro botões, sem capturar Start, Select ou hotkey do Recalbox. Não presumir a posição física A/B/X/Y: no núcleo histórico, TIC A/B/X/Y correspondem a RetroPad B/A/Y/X. Use o diagnóstico para identificar o gabinete.

O kumite usa **pontuação**, não barra de vida: primeiro a 5 pontos vence. Socos valem 1 e chutes 2 neste experimento. Contato válido pausa a ação por 1 segundo e recoloca os lutadores na distância inicial. Defesa não pontua. Empates simultâneos são possíveis.

A função `DD.judge(event, move)` recebe técnica, atacante/alvo, distância, zona, qualidade, resultado e frame. A qualidade atual é uma aproximação de distância ideal, não medição biomecânica nem arbitragem oficial Shotokan. Os quatro golpes usam desenhos esquemáticos e a mesma zona chudan; não há ainda diferenciação anatômica das trajetórias. Isso permite trocar futuramente os critérios sem reescrever entrada, movimento ou renderização.

## Jogar no notebook Linux

Ferramentas de desenvolvimento: Python 3.9+, GCC, Git e Tk para Python (`python3-tk` em distribuições Debian). Os downloads abaixo só são necessários para preparar as dependências uma vez. É possível obter o cartucho já pronto sem instalar compilador.

Na raiz **do repositório**:

```sh
python3 prototypes/tic80/tools/build_runtime.py
python3 prototypes/tic80/tools/play_notebook.py
```

O primeiro comando compila um núcleo Lua local com as APIs e loader históricos. Ele não instala nada no sistema ou no fliperama. Dependências fixadas em `tools/runtime-lock.json`, guardadas em `.cache/tic80-legacy/`. A revisão histórica referenciada pelo Recalbox tem um submódulo upstream indisponível; usamos Lua 5.3.1 e dependências GIF/blip públicas fixadas para validação Lua. Não é o binário ARM original nem uma reprodução integral de todos os interpretadores.

Após preparar, o segundo comando funciona **offline**. O viewer usa Python/Tk e o núcleo local, sem pacotes Python externos. Seus controles:

| Jogador | Direções U/D/L/R | A/B/X/Y |
|---|---|---|
| P1 | Setas | Z / X / A / S |
| P2 | I / K / J / L | F / G / R / T |

P1 Z+X por 1s troca tela; A+S por 1s reinicia. Esc fecha. Clique na janela para foco. Teclados podem ter ghosting em combinações; isso não demonstra falha de dois controles independentes.

Para usar joysticks USB já disponíveis no notebook, abra o cartucho no RetroArch com o núcleo TIC-80 e configure **apenas o notebook** para RetroPad nos usuários 1 e 2. O viewer simples acima recebe teclado, não joysticks USB.

Windows/macOS: abrir o `.tic` em uma instalação TIC-80/RetroArch apropriada é um caminho de teste, mas não foi validado aqui. O script de compilação acima é Linux; não declarar portabilidade do `.so`. O viewer aceita `--core /caminho/do/nucleo`, mas o formato e dependências devem corresponder ao sistema. Um TIC-80 moderno não substitui o teste do núcleo antigo.

## Reconstruir e testar offline

```sh
python3 prototypes/tic80/tools/build_cart.py
python3 prototypes/tic80/tools/build_runtime.py --offline
python3 prototypes/tic80/tools/test.py
```

O cartucho usa chunks legados não comprimidos: código tipo 5 e paleta tipo 12, banco 0. A geração exige só Python padrão. `build_runtime.py --offline` exige fontes previamente disponíveis e não busca nada na rede. Não enviar a árvore `.cache` ao cartão do fliperama.

Testes: integridade/cartucho atualizado, 14 casos de combate com Lua 5.3.1 e 6 grupos sobre entrada/renderização no núcleo histórico. O teste libretro cria em memória um cartucho auxiliar com telemetria `pmem`; esse recurso **não existe no cartucho entregue** e nenhum save é escrito pelo host de teste. Resultados visuais em `.cache/tic80-legacy/results/`.

Para validar o viewer sem monitor, se Xvfb já estiver disponível:

```sh
xvfb-run -a python3 prototypes/tic80/tools/play_notebook.py --frames 120
```

## Testar depois no Recalbox 6.1

1. Com alimentação estável e acesso ao cartão, identificar a instalação e fazer backup completo verificável em armazenamento já disponível. Sem backup ou enquanto persistir baixa tensão, não escrever no cartão.
2. Confirmar TIC-80 e os controles P1/P2 existentes. A árvore oficial do Recalbox 6.1 referencia a pasta `/recalbox/share/roms/tic80`; confirmar esse caminho na instalação real antes de copiar.
3. Copiar **somente** `dist/deshi-dojo.tic` como novo arquivo, sem substituir nomes existentes. Se o mesmo nome já existir, escolher outro nome. Não instalar o `.so` x86, atualizar Recalbox, substituir núcleo, remapear GPIO ou alterar configurações globais.
4. Abrir pelo sistema TIC-80 no menu existente; pode ser necessário atualizar a lista de jogos usando a função do próprio menu.
5. No diagnóstico: testar as quatro direções e quatro ações, P1 isolado, P2 isolado, ambos simultaneamente e diagonais. Registrar correspondência física sem alterar a configuração global.
6. Alternar a tela e testar golpes dos dois lados, defesa, colisão, vitória e reinício. Testar a hotkey original de retorno ao menu.
7. Rodar por 10–15 minutos, verificar fluidez, latência, temperatura e avisos de tensão; testar novamente jogos existentes. Desconectar a rede para confirmar a execução offline.

Se falhar, registrar erro, versão/hash do núcleo e qual entrada não chegou. Parar e investigar no notebook; não substituir componentes do sistema como tentativa. A remoção apenas do novo cartucho reverte a adição; alterações automáticas do frontend, se ocorrerem, devem ser verificadas contra o backup.

## Próximos passos

Confirmar alimentação e dois controles no gabinete; depois evoluir regras de pontuação, distância e precisão com o dojo, ajustar sprites e temporização. Ainda não há atletas reais, salto/agachamento no combate, animações definitivas, áudio, relógio de round ou regras oficiais de competição.
