# Lutro v05 — evidências e limites

Atualização de 11/10/2026 UTC. Combate e estudo de fundamentos em `games/shotokan-lutro-visual/`; independente dos projetos IKEMEN/TIC-80 preservados. Backup completo da versão Lutro v01 em `archives/shotokan-lutro-visual-v01.zip`, com manifesto SHA-256. Não houve acesso ao cartão, rede do gabinete ou modificação de jogos/configurações do fliperama.

## Implementado

Três ações nos dois ports: B soco, Y defesa, A chute; direções relativas ao adversário. Oito ataques ativos no chão, dois no salto, quatro uke e guarda neutra. Foram importadas 92 poses; animações confusas ficam preservadas fora dos comandos ativos. A barreira entre corpos mantém a ordem anterior ao movimento, incluindo avanços, pulos e paredes; corrigiu o atravessamento. Preparação mais curta, buffer de 24 ticks através dos bloqueios temporários, recuo, poses de impacto e combos por acertos consecutivos.

A luta usa energia, 60 segundos e dois rounds vencidos; treino/demonstração não limitam energia/tempo. Eventos de técnica e coordenadas do contato são emitidos por `Scene.onContact`, independente dessas regras, para permitir pontuação técnica futura. Não há arbitragem oficial. Catálogo JSON gera Lua único para cartucho/browser. O HTML ensina três ações na tela da luta e deixa as explicações completas em um painel opcional. Ver [FUNDAMENTOS.md](FUNDAMENTOS.md).
A v05 acrescenta CPU nos três níveis solicitados: vermelha/fácil, laranja/médio, preta/difícil. Inicia no fácil; escolha pelo browser ou F2/Select/direcional no jogo. Dois jogadores, treino e demonstrações continuam disponíveis. O controlador devolve botões para o mesmo combate, sem bônus de energia/dano, leitura de comandos futuros ou serviço externo. Histórico curto de observação; observação/decisão/erro e sequências variam por nível. Ver [CPU.md](CPU.md) para os perfis e as limitações de balanceamento. As faixas são indicadas no HUD/menu; a arte original permanece preservada.

## Núcleo e APIs históricas

Recalbox `6.1-Dragonblaze`, commit **8ffdef58cf5a555451581c6cf7a8bee33b0ed07c**, habilita `BR2_PACKAGE_LIBRETRO_LUTRO=y` na configuração Pi 3. O pacote fixa **a031f95394440022a561ce593d578474ac119c05**. Fontes primárias e declarações estão em `research/lutro/README.md`. Isso confirma a configuração oficial, não o conteúdo do cartão existente.

Testes usam essa revisão compilada para Linux x86-64 com Lua interpretado, `-fcommon` para o compilador atual, sem alterar fontes do motor. Renderização software XRGB8888. APIs exercitadas: `lutro.conf/load/update/draw`, `graphics.newImage/newQuad/draw/setColor/rectangle`, Lua 5.1 `require` e `joystick.isDown` nos dois ports.

Limitações tratadas:

- Entradas `isDown` atualizadas após update/draw, com atraso de um tick; o HTML reproduz a ordem. `input.joypad` tem problema de contagem de argumentos que impede selecionar a segunda porta e não foi usada.
- Blitter com transparência binária, sem tint/escala de PNG. Imagens finais opacas/transparentes, orientação espelhada já preparada e fonte em PNG. Sem shaders/APIs recentes.
- Checkout Windows: a conversão automática LF→CRLF do Git alterava o hash do Fengari e impedia iniciar o servidor. `.gitattributes` preserva seus bytes; o build repara clones antigos somente se os bytes restaurados corresponderem ao SHA-256 original. O teste `tests/windows_checkout.py` exercita LF/CRLF, repetição e rejeição de conteúdo modificado mesmo com `python -O`. A conversão foi reproduzida em Linux; isso não representa teste de um sistema Windows real.
- Loader `.lutro` exige diretórios explícitos antes dos arquivos; o pacote contém `assets/` e foi carregado por esse extrator.
- O core conserva canvas/framebuffer depois de `retro_deinit`; reinitializar a mesma imagem de biblioteca causou falha nativa. O host de testes usa cópia privada e byte-idêntica do `.so` por instância, carregando globals novos, sem patch. Saída/reabertura no frontend real ainda precisam de teste.

## Validação da versão atual

| Verificação | Evidência atual |
|---|---|
| Cartucho sem instrumentação | Loader histórico/PNGs, 384×224 e 600 ticks adicionais de movimento |
| Comandos/poses | 56 casos: 14 técnicas × 2 portas × 2 orientações |
| Colisão | 680 verificações por tick, ambas orientações, alvo parado, saltos; propostas de atravessamento extremas e paredes |
| Cobertura/energia | 40 pares no chão; defesa por linha efetiva do alvo; bloqueio não perde energia |
| Aplicações aéreas | 10 pares com defesas; altura efetiva, contato único e pouso |
| Combo básico | Quatro combinações porta/orientação com presses físicos antecipados: soco > soco > chute gera três contatos e 3 COMBO |
| Mecânicas | Botão mantido, distância, contatos simultâneos, recepção/timing, contra-ataque da defesa, reação/recuo, input através de pausa/stun, base baixa |
| Partida | KO, timeout, empate, round seguinte, vitória com dois rounds; treino preserva energia/tempo e eventos técnicos |
| Browser offline | 12 grupos: teclado real, colisão por quadro, quatro uke, soco/chute, combo, salto/pouso, treino/luta/estudo, entrada gamepad **simulada**, Enter/foco e RAF/Escape; zero HTTP externo/erros JS |
| CPU nativa | Sete grupos, três partidas autônomas completas, carga comum nos três perfis, atraso/inputs comuns, defesa real, isolamento do port2, menu nos dois ports e 1.080 ticks de replay Lua5.1/Fengari |
| CPU browser | Cinco grupos com seletores/teclado reais, solo/níveis, treino/demonstração/revanche, menu, retorno aos dois jogadores; offline/sem erros |
| Raster | 92 cenas/poses/bordas pixel a pixel nativo/browser; 92 poses espelhadas verificadas; três HUDs CPU/quatro opções de menu; regressão do pé 35/36 |
| Viewer desktop | 120 ticks em Xvfb, concluídos |
| Localhost | Página HTTP do servidor real, teclado dos dois jogadores/combo, hash do HTML, HEAD/no-store e acesso limitado à página; nenhuma requisição externa |
| Capturas | Cartucho entregue sem telemetria: 14 técnicas × 80 ticks, sequência básica adicional; PNG/GIF |
| Desempenho desktop | 1.800 ticks medidos; simulação/desenho, excluindo conversão RGB Python/monitor; `native-results.json` |

Resultados em `native-results.json`, `browser-results.json`, `raster-results.json`, `capture-results.json` e `web-server-results.json`, `cpu-native-results.json` e `cpu-browser-results.json` vinculam hashes aos artefatos. O teste Windows CRLF/integridade também passou.
Testes de lógica acrescentam telemetria apenas em uma fixture temporária, sem mudar cartucho/Lua entregues. Capturas executam o cartucho diretamente. Resultados JSON carregam hashes do artefato quando aplicável. Benchmarks x86-64 não demonstram 60 Hz no ARM; pausas do escalonador cloud também podem afetar máximos. Não há medição física de input lag ou sincronização do monitor.

## Memória conhecida

| Buffer gráfico | Bytes |
|---|---:|
| Atlases direito/esquerdo: 896×3312×4×2 | 23.740.416 |
| Fundo: 384×224×4 | 344.064 |
| Framebuffer: 384×224×4 | 344.064 |
| Fonte + sombra | 15.664 |
| Soma desses buffers | 24.444.208 |

Células de 224×144 contêm os membros completos. O defeito do mawashi vinha antes do atlas: a folha original cruzava uma divisória. A extração por figura recupera o pé e elimina o fragmento do quadro seguinte. Testes verificam essa regressão, espelhamento e renderização nas bordas. Importação rejeita silhuetas cortadas pelo quadro final. Cerca de 23,3 MiB nesses buffers não é RSS total; Lua, frontend, driver, decodificação, estruturas auxiliares e cópias não estão incluídos. Fontes de autoria grandes/poses PNG individuais ficam fora do `.lutro`. Não há prova de consumo total no Pi.

Arte gerada é uma interpretação ilustrativa, não execução biomecânica certificada. O jogo usa estados/caixas discretos, não articulações contínuas. Ainda faltam revisão técnica das poses/transições, personagens reais, áudio, arbitragem oficial e seleção de elenco. Resultado/revanche básica está implementado. Os projetos anteriores permanecem disponíveis; qualidade de jogabilidade precisa também de avaliação por jogadores.

## Testes futuros no gabinete

Confirmar presença/versão do core no cartão, espaço disponível e lançamento real, ARM, duas portas GPIO e três botões simultâneos, frequência/latência de vídeo, temperatura, memória total e saída/reabertura. Resolver os avisos de baixa tensão antes de medir desempenho.

Obter acesso ao cartão e backup verificável antes de transferir. Identificar o caminho instalado para Lutro; adicionar somente o novo cartucho sem sobrescrever jogos/configurações, atualizar sistema ou alterar GPIO. Não copiar bibliotecas x86 ao Raspberry Pi. Compatibilidade física/adopção final permanecem pendentes.

A versão Lutro v02 também continua recuperável pelo commit Git `1498e2d24faa8f5d17a39d3d82fe28774aea12d2`.

A versão Lutro v03 permanece recuperável no commit Git `2017b2c5b501a0472fb8955ecf97c18c570eb57a`. Nenhuma fonte antiga foi apagada.

A versão de combate v04 fica recuperável no commit `49b0d080e4ccfd5e7a4709c32b3c10fb1b8e58a3`. A CPU não alterou os sprites ou o repertório de técnicas.
