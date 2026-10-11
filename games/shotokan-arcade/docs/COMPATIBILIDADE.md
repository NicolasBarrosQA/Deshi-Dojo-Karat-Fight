# Versão 02 — melhorias, testes e compatibilidade

Validada em 11/10/2026 no ambiente cloud Linux x86-64. Nenhum acesso/gravação no fliperama, cartão ou notebook pessoal. A versão anterior foi preservada integralmente em `archives/shotokan-arcade-v01.zip` com manifesto SHA-256.

## Melhorias observáveis

| Área | V01 | V02 |
|---|---|---|
| Arte/personagens | 15 poses; silhuetas semelhantes | 33 poses cada, largura de corpo/jaw diferentes, dobras e faixa/ombros orientados com o torso; perfis editáveis de aparência |
| Respiração/caminhada | 2 quadros cada | 3 poses de respiração, 4 de avanço, recuo com mudança de apoio; pés preservam o piso |
| Cada técnica | Preparação e extensão; recuperação compartilhada | Antecipação, intermediário, extensão, recolhimento próprio e retorno à guarda |
| Oi-zuki | Avanço imediato de 4 px | Avanço distribuído pelos 9 ticks de preparação |
| Gyaku-zuki | Mudança direta de braço | Quadros de rotação de torso/faixa/ombros e retração do braço |
| Mae-geri | Câmara e extensão | Joelho sobe, perna abre, estende e recolhe antes de voltar ao solo |
| Mawashi-geri | Câmara e perna mais alta | Câmara, passagem mais alta, extensão lateral e recolhimento em trajetória projetada em 2D |
| Impacto/defesa | Reação efetiva; bloqueio sem pose própria | Hurtbox por pose, duas reações de bloqueio e impacto, efeitos curtos, 3/5 ticks de hitstop |
| Tempo e distância | Recuperação fixa | Erro expõe recuperação para contra-ataque, buffer curto de uma entrada recente; botão mantido não encadeia ataques |
| Apresentação | HUD simples e resultado cobrindo lutadores | Faixas no HUD/seleção, PRONTOS/HAJIME, resultado com poses de vitória/derrota visíveis, revanche protegida contra confirmação acidental |
| Cenário | Tatame e janelas mais claros | Fundo menos contrastante, textura reduzida, elementos de madeira refinados e sombras mais próximas dos pés |
| Áudio | Ausente | 7 envelopes originais: passos, soco, chute, bloqueio, contato, ponto e vitória |

[Comparação real v01/v02](comparison.png) e [GIF contínuo](kumite-execution.gif). O GIF mostra postura, avanço/recuo, P1 oi-zuki, P2 gyaku-zuki, P1 mae-geri e P2 mawashi-geri numa mesma partida, encerrando a sequência em 3–3. Capturas vêm do cartucho entregue, sem alteração de lógica nem telemetria.

## Memória e APIs históricas

Alvo continua TIC-80 **0.80.0-dev**, commit `b3e158c15997beba019aa02cfad3c7d70caca84e`, fixado pelo Recalbox `6.1-Dragonblaze` (`8ffdef58cf5a555451581c6cf7a8bee33b0ed07c`). O núcleo consta na configuração oficial Pi 3; o cartão instalado pode ser diferente.

| Recurso | Uso |
|---|---:|
| Resolução/paleta | 240×136, 16 cores compartilhadas |
| Tiles lógicos originais | 929, deduplicados entre poses/personagens |
| Tiles residentes no atlas físico | 480 / 512, 15.360 bytes |
| Cache de desenho | Tile físico 480, 32 bytes; copiado antes de cada uso e desenhado imediatamente |
| Fundo na área de mapa | 16.320 bytes |
| Tiles adicionais na área de mapa | 449 × 32 = 14.368 bytes |
| Área de mapa total | 30.688 / 32.640 bytes; 1.952 bytes livres |
| Código Lua banco 0 | 38.086 / 65.535 bytes |
| Áudio | 7 × 66 bytes de SFX + 32 bytes de ondas = 494 bytes |
| Cartucho completo | 84.704 bytes |

O limite de 512 tiles **não foi alterado**. Os tiles adicionais são dados em memória de mapa, copiados para um slot físico com `memcpy(0x7c00,0xbfc0+(id-480)*32,32)` antes do `spr(480,...)`. Fundo usa `memcpy(0,0x8000,16320)`. Isso foi exercitado no loader/memória/desenho históricos e comparado pixel a pixel com o adaptador HTML. Um tilemap convencional não pode ocupar simultaneamente essa mesma área. Temos pouco espaço restante; mais animações ou elenco exigirão compartilhar partes, reorganizar memória ou reavaliar o motor.

APIs do cartucho: `TIC`, `btn`, `spr`, `memcpy`, `rect`, `rectb`, `line`, `print`, `sfx` e funções padrão Lua. Sem `vbank`, `BOOT`, bancos extras, compressão de código, persistência, shaders, bibliotecas externas ou rede. SFX usa o formato de 66 bytes, ondas de 4 bits e flags de mute estéreo históricas em zero. O HTML embute o mesmo Lua, tiles, cenário, paleta, fonte e definições de áudio; WebAudio aproxima a síntese, sem afirmar igualdade PCM.

O runtime de validação reutiliza o núcleo Lua-only x86-64 preparado no protótipo original. O submódulo `nesbox/3rd-party` original ficou indisponível; loader/core/API Lua/libretro são do commit histórico, sem alteração, com dependências públicas fixadas. Não é reprodução integral do binário ARM do Recalbox. A investigação detalhada e limitações estão em `prototypes/tic80/docs/COMPATIBILIDADE.md` na raiz do repo.

## Testes executados

| Verificação | Resultado |
|---|---|
| 28 testes Lua 5.3.1 | Passaram: funcionalidades anteriores, todos os golpes em ambos os lados, fases, defesa, simultaneidade, timer, seleção, revanche, 6.000 ticks aleatórios e novas regressões |
| Quatro grupos de integração no núcleo histórico | Passaram: chunks/código/SHA-256/cache/áudio dentro dos limites, 16 inputs separados, movimento simultâneo, contato único, pontuação simultânea, vitória, revanche, timeout completo de 3.600 ticks e empate |
| Cartucho sem instrumentação | 13 capturas de telas/técnicas/bloqueio e GIF contínuo produzidos |
| Áudio histórico | 7 efeitos produziram PCM não zero, sem clipping de 16 bits; [WAV do núcleo](original-effects.wav) e `audio-results.json` |
| HTML no Chromium offline | Passou seleção, teclado P1/P2, movimento simultâneo, quatro golpes para cada jogador, pontuação, menus, som WebAudio e mute |
| Raster da tela inicial browser/nativo | Idêntico pixel a pixel em 240×136; não implica equivalência de todos os timings |
| Viewer Tk/Linux | Passou: 120 frames em Xvfb; esse host de desenvolvimento descarta áudio |
| Estabilidade/CPU | 7.080 frames medidos por versão em núcleo x86-64; ver `performance-results.json` |
| HTML CPU/cadência | 1.200 updates e cadência real de RAF/teclado, em `browser-performance-results.json` |

A integração lê estados por `pmem` acrescentado somente a uma cópia em memória; a prova de áudio também acrescenta um acionamento sequencial em memória. Nada disso integra o `.tic` entregue. Os capturadores e o viewer abrem o arquivo distribuído diretamente. O WAV comprova saída PCM do núcleo, não saída do alto-falante físico.

Medição final do núcleo: v01 média **0,183 ms**, p99 **0,821 ms**; v02 média **0,282 ms**, p99 **4,252 ms**, máximo **9,492 ms**, nenhum frame acima de 16,67 ms e nenhum erro Lua. O teste inclui desenho/áudio do núcleo, exclui conversão RGB Python, monitor e latência dos controles. A variação de processos da nuvem afeta esses valores; não afirmar ganho de velocidade nem extrapolar ao ARM.

No HTML headless: média **1,96 ms**, p99 **8,80 ms** por update. Houve **2 de 1.200** updates acima de 16,67 ms, máximo **146,2 ms**; portanto há pausas ocasionais no ambiente, apesar da cadência observada de **121 ticks em 2.015 ms**. O motor browser tem custos/GC próprios e não representa desempenho do fliperama.

## Qualidade desejada e limite real do TIC-80

As animações e a apresentação evoluíram sobre a base anterior. As capturas mostram membros preenchidos, textura de gi, silhuetas distintas, movimento de corpo, recolhimento e resultados expressivos. Os rostos continuam com poucos pixels e os quadros intermediários são limitados; a qualidade atual ainda não corresponde ao objetivo de representar os alunos com o detalhe de sprites de Street Fighter. Simples ampliação do HTML ou dos PNGs não recupera informação facial.

A prioridade informada pelo usuário é investigar resolução maior com Pi 3 e custo zero. **Recomendo Lutro como próximo candidato**, sem migração automática: está habilitado na configuração Pi 3 oficial do Recalbox 6.1, e a revisão histórica passou numa prova x86-64 em **384×224**, preservando um PNG de **30.720 cores** e dois jogadores independentes. Isso remove os limites gráficos identificados, mas não comprova o jogo no Pi.

O alvo proposto é arte original em resolução nativa, sprites de aproximadamente 96–128 px de altura, fotografias autorizadas como referência de cabelo/rosto/biotipo e animações com o orçamento real de memória. `src/characters.json` separa proporções, cabelo, tons e faixa; esses perfis podem orientar a futura arte, sem gerar automaticamente uma semelhança facial convincente. O relatório, código e teste da investigação estão em `research/lutro/README.md` na raiz do repo. Nenhum sprite de franquia foi usado.

A trajetória tridimensional dos chutes, pivô e precisão técnica ainda devem ser revisados por um instrutor. `G.judge` continua substituível: contato, técnica, distância, qualidade aproximada, zona chudan e estado de contra-ataque entram no evento; não é regulamento oficial. Não há vida sendo reduzida. O dojo é estático; o painel é ornamental, não caligrafia validada.

## Pendências físicas

Ainda não validados: executable ARM instalado, presença real dos núcleos no cartão, 60 Hz estáveis, temperatura, alimentação, memória total do processo, monitor LG, GPIO e combinações dos dois jogadores, áudio físico, hotkey de saída e regressão dos jogos antigos. Não houve alteração do fliperama.

Antes de transferência: resolver baixa tensão, fazer backup verificável e identificar versões/espaço disponíveis. Não atualizar Recalbox, drivers, núcleos, reserva de GPU ou overclock para tentar passar nos testes. Adicionar somente o `.tic` após esses preparativos e testar controles/saída antes de uma partida.

Capturas adicionais: [título](title-4x.png), [seleção](selection-4x.png), [hajime](hajime-4x.png), [kumite](kumite-4x.png), [oi](oi-zuki-4x.png), [gyaku](gyaku-zuki-4x.png), [mae](mae-geri-4x.png), [mawashi](mawashi-geri-4x.png), [bloqueio](block-4x.png), [resultado](result-4x.png), [revanche](rematch-4x.png), [diagnóstico](diagnostic-4x.png). PNGs nativos 256×144 incluem borda libretro; ampliações usam nearest-neighbor.
