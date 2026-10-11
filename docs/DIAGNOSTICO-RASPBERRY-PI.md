# Shotokan Arcade — diagnóstico para Raspberry Pi 3

Data: 10/10/2026. Meta: Raspberry Pi 3 Model B rev. 1.2, Recalbox 6.1 DragonBlaze, custo zero, partidas offline, dois jogadores e preservação do sistema existente.

## Conclusão

Priorizar um protótipo TIC-80 em Lua, distribuído como cartucho `.tic` para o núcleo libretro já existente **se sua presença e compatibilidade forem confirmadas**. Preservar a base IKEMEN como referência e alternativa para PC. Não instalar outro sistema, atualizar Recalbox, substituir núcleos nem alterar GPIO nesta etapa.

Esta é uma escolha técnica condicionada, não uma certificação de funcionamento no gabinete. O suporte TIC-80 no Recalbox 6.1 foi informado na investigação presencial; não foi possível confirmar nesta pesquisa o commit ou binário dessa versão antiga. A documentação e o código atuais do TIC-80 não comprovam recursos de um núcleo de 2019.

## Estado real do projeto

Inspeção do checkout `/workspace/Deshi-Dojo-Karat-Fight`:

- `engine/engine.json`: IKEMEN GO 1.0.0 fixado, downloads e SHA-256 oficiais para Linux e Windows x86-64.
- `scripts/install.py`: download, verificação, extração e reutilização de instalação existente.
- `scripts/run.py`: aplicação dos arquivos de `game/`, início do motor, demo e teste de combate.
- `scripts/setup-cloud.sh` e `smoke-cloud.sh`: ambiente gráfico virtual para validação Linux Debian 13.
- `licenses/` e `docs/ASSETS.md`: licenças e atribuições do motor e recursos de exemplo.
- `game/chars`, `stages`, `data`, `sound`: contêm somente README; nenhum conteúdo original jogável.
- `.runtime/`: distribuição oficial, personagem Kung Fu Man, cenários e interface de exemplo; ignorada pelo Git.
- `.cache/smoke/`: resultados de testes anteriores. O resultado `match-1791642279387680496.txt` registra um round, 600 ticks, dois KFM, vida 775/900 de 1000 e um vencedor.

A validação anterior foi em Linux x86-64 na nuvem, com Xvfb e OpenGL 4.5 por Mesa llvmpipe. Não ocorreu no notebook do usuário nem no Raspberry Pi. Nesta investigação, os arquivos e resultados foram inspecionados; não houve novo teste físico.

Não existem ainda alunos digitalizados, animações Shotokan, sistema próprio de combate, cartucho TIC-80 ou teste de controles humanos simultâneos. Windows não foi validado. Os arquivos do projeto continuam locais e não foram enviados ao GitHub nesta tarefa.

## Comparação de alternativas

| Alternativa gratuita | Vantagem | Obstáculo neste gabinete | Prioridade |
|---|---|---|---|
| IKEMEN GO 1.0.0 atual | Estrutura especializada de luta, ferramentas/formato MUGEN | Binário instalado x86-64; instalador rejeita ARM. Port exige toolchain/ABI e backend gráfico compatíveis com Recalbox antigo. VideoCore IV oferece GLES 2.0, não o OpenGL desktop 3.3 do caminho atual. Renderização por software não foi medida no Pi e é inadequada como aposta de desempenho. Não é um núcleo libretro para integração direta. | Preservar para PC; não usar como alvo principal |
| TIC-80 via libretro | Cartucho pequeno, gráficos de baixa resolução, entrada via RetroPad, ferramentas gratuitas, código MIT | Precisamos implementar o combate; núcleo antigo pode rejeitar cartucho/API modernos. Limites de sprites, cores e quatro ações. Desempenho e P2 no gabinete ainda desconhecidos. | Primeiro candidato |
| Lutro via libretro | Framework Lua 2D, mais liberdade de recursos e comandos | Experimental, API parcial de LÖVE; presença/versão no Recalbox 6.1 e P2 não confirmadas. Ainda exige combate próprio. | Plano B se já estiver instalado e passar um teste |
| Jogo homebrew para console já emulado (por exemplo Mega Drive) | Aproveita emulador e controles existentes; pode dispensar qualquer mudança de sistema | Toolchain e programação específicas, restrições gráficas; desenvolvimento muito mais trabalhoso. Núcleo exato e suporte a dois controles precisam ser identificados. | Plano C se TIC-80 não estiver disponível |
| LÖVE/SDL2 nativo ou Godot com backend adequado | Mais liberdade e ferramentas gratuitas | Compatibilidade de bibliotecas/ARM/GLES, execução fora da integração atual e entrada GPIO exigem investigação. Instalar bibliotecas ou atualizar o sistema contraria a estratégia de preservação. | Não priorizar agora |

MUGEN clássico e executáveis Windows não resolvem a arquitetura ARM nem a integração do gabinete. Não tratar emulação de x86 como solução de custo/desempenho para esse Pi.

## O que reaproveitar

- Reaproveitar organização, documentação, rastreabilidade de licenças e princípios de download verificado.
- Preservar IKEMEN para consultar estados de luta, temporização e testes. O protótipo TIC-80 terá instalação/execução separadas: os scripts x86-64 atuais não são instaladores do Recalbox.
- Personagens, artes e animações originais reaproveitáveis: **ainda não existem**. Nada desse trabalho foi perdido.
- Recursos KFM/MUGEN são referência não comercial, não assets Shotokan prontos. TIC-80 não lê `.sff`, `.air`, `.cns` ou `.cmd` diretamente; exportar/redimensionar/recolorir e reimplementar comportamento seria necessário. Para o protótipo, desenhar silhuetas originais é menor trabalho e evita dependência de KFM.
- As quatro técnicas escolhidas e o conceito de elenco do dojo continuam válidos. São requisitos, não regras implementadas.
- Animações futuras devem preservar poses/timing como dados de projeto; a renderização será pixel art compatível com TIC-80. Validar a identificação técnica dos golpes com o dojo.

## Arquitetura proposta, sem substituir IKEMEN

Criar futuramente uma pasta independente `prototypes/tic80/` com fonte Lua, recursos originais, licença e instruções para gerar um `.tic`. Manter `engine/`, `scripts/`, `game/`, `.runtime/` e documentação existentes intactos.

Fluxo no gabinete:

`controles existentes → driver já configurado no Recalbox → RetroArch/RetroPad P1 e P2 → núcleo TIC-80 → cartucho Shotokan`

O jogo não deve acessar GPIO diretamente, disputar pinos com o driver, usar rede ou exigir serviços externos. A presença aparente de fios no GPIO não confirma driver, pinagem ou dois dispositivos independentes. Identificar a configuração existente posteriormente, sem remapear globalmente.

Dentro do cartucho:

- Lua usando apenas APIs básicas confirmadas no núcleo alvo: `TIC`, leitura `btn`, desenho simples e, depois, `spr`/áudio básico.
- Simulação com passo fixo, meta 60 atualizações/segundo, posições em coordenadas lógicas 240×136.
- Dois lutadores com máquina de estados: parado, deslocamento, ataque (preparação/ativo/recuperação), defesa, reação ao golpe e derrota.
- Dados de golpe: alcance, hitbox, dano, duração por fase e recuperação. Separar dano de desenho; um golpe acerta uma vez por execução.
- Hitboxes/hurtboxes retangulares, sem física geral, sem shaders, sem partículas numerosas. Resolver ataques simultâneos a partir do estado dos dois jogadores para não privilegiar P1 pela ordem de atualização.
- Vida e limite de arena; defesa segurando direção oposta ao adversário; sem regras de pontuação de competição neste primeiro jogo arcade.
- Um cenário estático, mesma base de personagem com duas paletas, sprites pequenos compostos de tiles. Começar em um banco, sem APIs avançadas, cartuchos comprimidos ou formatos recentes até verificar o núcleo antigo.
- Sem inteligência artificial, multiplayer online, seleção extensa, história, ranking ou salvamento no primeiro protótipo.

O cartucho TIC-80 não é um motor de luta pronto. A economia está no runtime, distribuição e integração libretro; combate e animação continuam sendo trabalho do projeto.

## Menor protótipo e critérios de aceitação

### Etapa 0 — cartucho de diagnóstico

Uma tela com indicadores P1/P2 para quatro direções e quatro ações; contador de frames e movimento simples dos dois avatares. Sem áudio inicialmente.

No notebook: testar todas as entradas, simultaneidade e independência de P1/P2 no TIC-80 e no RetroArch com núcleo de versão identificada. Um teclado comum pode ter ghosting: falha simultânea de teclas não prova defeito do cartucho. Registrar versão e hash do núcleo e cartucho. Se o binário do gabinete puder ser identificado, buscar a revisão correspondente para testes locais; um núcleo x86 da mesma revisão ainda não prova desempenho ARM.

No gabinete: confirmar abertura do `.tic`, direções, diagonais, quatro botões de cada jogador, entradas simultâneas, retorno ao menu e ausência de mudanças nos jogos existentes. Somente depois disso investir em sprites dos alunos.

### Etapa 1 — luta mínima Shotokan

- Dois jogadores humanos, dois avatares originais simples e um cenário.
- Quatro botões de ação: oi-zuki, gyaku-zuki, mae-geri e mawashi-geri. Direções para deslocamento/defesa; não depender de seis ações independentes.
- Oi-zuki com avanço controlado, gyaku-zuki como soco reverso, mae-geri frontal e mawashi-geri circular. Representação estilizada a revisar com o dojo; valores de equilíbrio ainda não definidos.
- Hitboxes, defesa, reação, recuperação e barra de vida; um round e reinício por combinação de ações após a derrota.
- Tela de vitória e teste de funcionamento inteiramente offline.

A entrada normal TIC-80 tem oito bits por jogador: quatro direções + A/B/X/Y. Os seis botões físicos não significam seis ações disponíveis nesse núcleo. Os dois restantes podem ficar sem uso no cartucho; Start/Select/hotkey devem conservar sua função existente. Usar a ordem lógica A/B/X/Y, sem presumir posição física: há diferenças de nomenclatura entre TIC-80 e RetroPad. Não capturar a combinação de saída do Recalbox.

Testes locais úteis: ataque só durante frames ativos, um dano por golpe, defesa pela direção correta, recuperação impede novo ataque, colisão de arena, vitória/reinício e simetria de P1/P2. Medir comportamento em 60 ticks simulados por segundo e registrar os resultados. Nesta entrega esses testes são propostos; o cartucho não foi implementado nem validado.

## Recursos e desempenho

1 GB inclui sistema, RetroArch, reserva de GPU e o jogo; não é memória integralmente disponível. TIC-80 restringe principalmente recursos do cartucho e execução de scripts, e seu consumo real inclui Lua/núcleo/frontend. Não afirmar que ocupa só a memória virtual do cartucho.

240×136, paleta de 16 cores e quatro canais de áudio são limites documentados do TIC-80 atual; limites e bancos da versão antiga precisam ser conferidos. Usar orçamento conservador de sprites, reutilização de paletas e animações curtas. Evitar alocação de tabelas por frame, acesso a arquivos durante luta e animações em alta resolução.

O quad-core não implica paralelismo automático: lógica Lua/core pode ser limitada por uma thread. Meta 60 fps, aproximadamente 16,7 ms por frame; um resultado no notebook não prevê desempenho no Pi. Se houver queda, reduzir renderização e efeitos antes de aumentar escopo. 30 fps só como alternativa explícita, com temporizações revistas e aceitação da perda de fluidez.

## Verificações físicas pendentes

- Confirmar versão real/arquitetura do Recalbox, presença do núcleo TIC-80, sua revisão e extensão/pasta aceitas. Não inferir compatibilidade pelo menu ou pela documentação atual.
- Identificar capacidade, espaço livre e condição do microSD. Antes de qualquer escrita, produzir uma imagem completa de backup verificável em armazenamento já disponível; preservar configurações e ROMs. Se não houver espaço/meio para backup, parar a instalação e continuar desenvolvimento local.
- Sem atualizar/reinstalar: acrescentar apenas o novo cartucho na pasta já suportada, sem substituir ROMs, núcleos, listas ou configurações globais. Caminho exato depende da instalação identificada.
- Identificar driver GPIO, mapeamento e portas P1/P2; verificar seis botões físicos e quais quatro chegam ao TIC-80. Não mudar pinagem nem adicionar driver.
- Verificar saída HDMI, escala, proporção, áudio, latência e overscan no monitor LG.
- Medir 60 fps, ritmo de áudio e resposta dos dois controles durante pelo menos 10–15 minutos; verificar temperatura, throttling e avisos de baixa tensão.
- Baixa tensão pode provocar lentidão, instabilidade e comprometer operações de escrita. Com o aparelho desligado, conferir conexão e especificação da fonte/cabo existentes. Não usar overclock como correção. Se a alimentação continuar inadequada e não houver alternativa já disponível, isso é um bloqueio físico sob orçamento zero, não um defeito resolvível no jogo.
- Testar entrada/saída do cartucho e novamente jogos existentes. Registrar alterações; remoção do cartucho deve reverter a adição. Nunca cortar a alimentação durante gravação.

Ausência de acesso por rede e teclado sem fio não funcional impedem inspeção remota agora, mas não tornam a rede necessária ao jogo. Preparar tudo localmente e usar posteriormente apenas um meio de transferência já disponível. Dependências de desenvolvimento podem ser obtidas previamente; as partidas devem funcionar sem downloads, autenticação ou conexão.

## Evidências e fontes

- Inspeção local: README.md, engine/engine.json, scripts/, game/, docs/VALIDATION.md, docs/ASSETS.md e resultado de combate citado acima.
- `file .runtime/1.0.0/linux/Ikemen_GO_Linux`: ELF 64-bit x86-64; não ARM.
- [IKEMEN GO 1.0.0](https://github.com/ikemen-engine/Ikemen-GO/tree/v1.0.0): motor compatível com recursos MUGEN. Os requisitos gráficos usados neste projeto também estão no README local.
- [TIC-80](https://github.com/nesbox/TIC-80): limitações gráficas, cartuchos, ferramentas, linguagens e licença. Não exigir assinatura Pro; avaliar as ferramentas gratuitas/compilação aberta para o processo de criação.
- [Documentação libretro TIC-80](https://docs.libretro.com/library/tic80/): `.tic`, sem BIOS, RetroPad, múltiplos jogadores e tabela A/B/X/Y.
- [Código atual da entrada TIC-80 libretro](https://github.com/nesbox/TIC-80/blob/main/src/system/libretro/tic80_libretro.c): leitura separada por porta. Evidência do código atual, não da versão instalada.
- [Documentação Lutro](https://docs.libretro.com/library/lutro/): framework experimental, formatos e suporte parcial.

Consultadas em 10/10/2026. Recursos de núcleo antigo, desempenho físico e instalação segura continuam pendentes de confirmação.
