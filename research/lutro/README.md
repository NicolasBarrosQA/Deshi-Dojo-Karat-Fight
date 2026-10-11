# Investigação: resolução maior sem trocar o hardware

Investigação solicitada em 11/10/2026. O jogo não foi migrado: esta pasta contém somente uma prova de capacidade do motor e suas evidências. `games/shotokan-arcade/` continua sendo a versão jogável TIC-80.

## Resultado concreto

A configuração oficial Recalbox `6.1-Dragonblaze`, commit `8ffdef58cf5a555451581c6cf7a8bee33b0ed07c`, habilita `BR2_PACKAGE_LIBRETRO_LUTRO=y` no Pi 3. O pacote fixa **a031f95394440022a561ce593d578474ac119c05**. Cópias das declarações estão em `games/shotokan-arcade/docs/recalbox61-lutro.mk.txt` e `recalbox-rpi3-defconfig.txt`.

Compilei essa revisão original para Linux x86-64, usando Lua interpretado, sem modificar as fontes. Foi necessário `-fcommon`, que restaura o comportamento padrão do compilador de 2019 para símbolos comuns. A revisão usa renderização por software e entrega framebuffer XRGB8888 ao frontend.

O teste real passou em **384×224 pixels**, com **30.720 cores distintas** de um PNG original preservadas pixel a pixel, 16 entradas verificadas separadamente (direções e quatro ações em cada porta), movimento independente e mais 600 frames sem erro. Veja `results.json` e `capture.png`. Essa imagem é uma calibração de resolução/cor/input, não arte definitiva nem uma migração do jogo.

O `lutro.joystick.isDown` histórico tem cache de um tick: as entradas são atualizadas depois de desenho/update. O teste registra esse atraso. A integração futura deverá avaliar eventos ou a API de entrada direta, mantendo consistência entre jogadores. O núcleo não fornece uma fonte de texto pronta nesta prova; uma fonte bitmap própria precisa ser carregada. A API é um subconjunto de LÖVE, portanto um projeto LÖVE moderno não pode ser considerado compatível automaticamente.

## Recomendação para a meta visual

**Lutro é o candidato prioritário para a próxima prova visual**, pois já consta no sistema oficial e remove os limites fixos de 240×136/16 cores/tiles do TIC-80. O alvo inicial proposto é 384×224, com arte original em resolução nativa e sprites de aproximadamente 96–128 px de altura, ajustados à interface. Ampliar os PNGs atuais não acrescenta detalhes de rosto: será necessário refinar a arte nessa nova resolução e depois adaptar os traços dos alunos a partir de fotografias autorizadas.

Esta etapa comprovou capacidade gráfica/entrada no núcleo x86-64; ainda não comprovou desempenho do jogo nesse motor, instalação efetiva no cartão ou comportamento ARM/GPIO. A presença do pacote oficial não prova a presença no gabinete. Antes de adotar, testar no núcleo histórico uma cena representativa com dois sprites detalhados, animações, transparência, áudio, hitboxes e 60 Hz; depois medir no gabinete com backup e alimentação adequada.

| Opção gratuita | Evidência disponível | Decisão |
|---|---|---|
| TIC-80 histórico | Jogo e testes atuais; núcleo oficial Pi 3 | Manter como versão preservada e jogável; resolução/cor restringem o objetivo de retratar os alunos |
| Lutro histórico | Habilitado na configuração Pi 3 do Recalbox 6.1; prova gráfica/entrada x86-64 executada | Priorizar investigação visual; adoção depende de cena de jogo e teste ARM |
| SDL2 com motor próprio | Configuração oficial inclui SDL2; APIs de desenho/entrada exigiriam integração própria | Alternativa de maior trabalho; executável/lançamento no Recalbox não validados aqui |
| IKEMEN GO | Projeto preservado; desenvolvimento x86 anterior | Exige investigar OpenGL/ARM/memória antes de considerar para Pi 3; não recomendado com a evidência atual |
| OpenBOR / LÖVE completo | Possíveis candidatos externos | Presença e integração neste Recalbox 6.1 não comprovadas; não prometer compatibilidade |

Não há compra, conta, ROM de franquia, alteração de GPIO, atualização de sistema ou gravação no fliperama nesta investigação.

## Reproduzir no ambiente de desenvolvimento

Na raiz do repositório:

```bash
python3 research/lutro/prepare.py
python3 research/lutro/test.py
```

Preparação inicial usa Internet, GCC/Make e fontes fixadas com SHA-256. Depois o teste funciona offline; Pillow é apenas ferramenta de captura/verificação. O `.so` fica em `.cache/lutro-research/source/`, não é distribuído para o fliperama e não deve ser copiado ao ARM.

Fontes primárias: [pacote Recalbox](https://gitlab.com/recalbox/recalbox/-/blob/8ffdef58cf5a555451581c6cf7a8bee33b0ed07c/package/libretro-lutro/libretro-lutro.mk), [configuração Pi 3](https://gitlab.com/recalbox/recalbox/-/blob/8ffdef58cf5a555451581c6cf7a8bee33b0ed07c/configs/recalbox-rpi3_defconfig), [Lutro libretro histórico](https://github.com/libretro/libretro-lutro/blob/a031f95394440022a561ce593d578474ac119c05/libretro.c), [gráficos](https://github.com/libretro/libretro-lutro/blob/a031f95394440022a561ce593d578474ac119c05/graphics.c), [input](https://github.com/libretro/libretro-lutro/blob/a031f95394440022a561ce593d578474ac119c05/joystick.c), [loop de update](https://github.com/libretro/libretro-lutro/blob/a031f95394440022a561ce593d578474ac119c05/lutro.c).
