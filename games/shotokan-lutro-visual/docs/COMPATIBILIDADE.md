# Lutro v03 — evidências e limites

Atualização de 11/10/2026 UTC. Combate e estudo de fundamentos em `games/shotokan-lutro-visual/`; independente dos projetos IKEMEN/TIC-80 preservados. Backup completo da versão Lutro v01 em `archives/shotokan-lutro-visual-v01.zip`, com manifesto SHA-256. Não houve acesso ao cartão, rede do gabinete ou modificação de jogos/configurações do fliperama.

## Implementado

Três ações nos dois ports: B soco, Y defesa, A chute; direções relativas ao adversário. Quatro uke por altura com trajetórias próprias, guarda neutra, gyaku médio/alto, oi, mae médio/baixo, mawashi médio/alto, kizami, yoko kekomi e ushiro. Há salto, base baixa, três aplicações aéreas e sequências de até três técnicas com retorno completo. Setenta e seis poses, fase exibida, separação de corpos, caixas por altura, hitbox pequeno apenas na extensão, preparação/recuperação, um contato por ataque, interrupção ao receber golpe e contatos simultâneos. Não há HP. Eventos registram técnica, altura, distância em pixels, tempo de recepção, contra-ataque, sobreposição, altura de salto e índice da sequência para futura avaliação; a contagem atual é experimental.

O catálogo JSON gera um módulo Lua usado tanto no cartucho quanto no HTML. O HTML oferece explicações, seletor de estudo, câmera lenta, pausa e quadro único, tudo offline. O cartucho também exibe nome/fase, mas não contém o painel explicativo do browser. [Fundamentos e fontes](FUNDAMENTOS.md) distinguem pesquisa consultada, convenções de jogo e revisão pelo instrutor ainda pendente.

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

| Verificação | Evidência |
|---|---|
| Cartucho entregue sem instrumentação | Carregou/desenhou 384×224, PNG do cenário preservado e 600 ticks adicionais de movimento |
| Comandos/poses | 68 casos: 17 técnicas × 2 portas × 2 orientações, todas as poses previstas atingidas |
| Cobertura por altura | 50 pares: 10 ataques × 4 uke + guarda neutra; linha correta bloqueia, linhas erradas não |
| Aplicações aéreas | 15 pares com defesas: linha efetiva do contato, um ataque por salto e aterrissagem |
| Sequências | 12 casos: três exemplos × duas portas × duas orientações; recolhimento completo e sem repetição por botão mantido |
| Mecânica adicional | Botão mantido sem repetição, distância, separação, contatos simultâneos, defesa tardia, recepção no tempo, contra-ataque marcado e mudança de direção reiniciando preparação |
| Browser offline | 11 grupos: salto, ataques aéreos, novas técnicas e sequências, além de teclado real nos dois jogadores, quatro uke, soco/chute, altura correta/incorreta, estudo/câmera lenta/pausa/quadro único e loop RAF real; zero HTTP externo/erros JS |
| Viewer desktop | 120 ticks em Xvfb, concluídos |
| Capturas | 1.360 ticks do cartucho entregue sem telemetria, cobrindo 17 técnicas; sequência extra; PNG/GIF reais |
| Raster | 69 cenas/poses/bordas nativo/browser comparadas pixel a pixel; resultado em `raster-results.json` |
| Desempenho desktop | 1.800 ticks medidos com simulação/desenho, excluindo conversão RGB do Python/monitor; métricas atuais em `native-results.json` |

Testes de lógica acrescentam telemetria apenas em uma fixture temporária, sem mudar cartucho/Lua entregues. Capturas executam o cartucho diretamente. Resultados JSON carregam hashes do artefato quando aplicável. Benchmarks x86-64 não demonstram 60 Hz no ARM; pausas do escalonador cloud também podem afetar máximos. Não há medição física de input lag ou sincronização do monitor.

## Memória conhecida

| Buffer gráfico | Bytes |
|---|---:|
| Atlases direito/esquerdo: 896×2736×4×2 | 19.611.648 |
| Fundo: 384×224×4 | 344.064 |
| Framebuffer: 384×224×4 | 344.064 |
| Fonte + sombra | 15.664 |
| Soma desses buffers | 20.315.440 |

Células de 224×144 contêm os membros completos. O defeito do mawashi vinha antes do atlas: a folha original cruzava uma divisória. A extração por figura recupera o pé e elimina o fragmento do quadro seguinte. Testes verificam essa regressão, espelhamento e renderização nas bordas. Importação rejeita silhuetas cortadas pelo quadro final. Cerca de 19,4 MiB nesses buffers não é RSS total; Lua, frontend, driver, decodificação, estruturas auxiliares e cópias não estão incluídos. Fontes de autoria grandes/poses PNG individuais ficam fora do `.lutro`. Não há prova de consumo total no Pi.

Arte gerada é uma interpretação ilustrativa, não execução biomecânica certificada. O jogo usa estados/caixas discretos, não articulações contínuas. Ainda faltam revisão técnica das poses/transições, personagens reais, áudio, arbitragem oficial, seleção e resultado/revanche nesta amostra; os projetos anteriores permanecem disponíveis.

## Testes futuros no gabinete

Confirmar presença/versão do core no cartão, espaço disponível e lançamento real, ARM, duas portas GPIO e três botões simultâneos, frequência/latência de vídeo, temperatura, memória total e saída/reabertura. Resolver os avisos de baixa tensão antes de medir desempenho.

Obter acesso ao cartão e backup verificável antes de transferir. Identificar o caminho instalado para Lutro; adicionar somente o novo cartucho sem sobrescrever jogos/configurações, atualizar sistema ou alterar GPIO. Não copiar bibliotecas x86 ao Raspberry Pi. Compatibilidade física/adopção final permanecem pendentes.

A versão Lutro v02 também continua recuperável pelo commit Git `1498e2d24faa8f5d17a39d3d82fe28774aea12d2`.
