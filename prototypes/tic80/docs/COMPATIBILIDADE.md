# Compatibilidade comprovada e pendente

Investigação e validação em 10/10/2026. Ambiente disponível: Linux x86-64 na nuvem, não o notebook pessoal nem o gabinete.

## Alvo histórico identificado

A tag oficial `6.1-Dragonblaze` do Recalbox aponta para `8ffdef58cf5a555451581c6cf7a8bee33b0ed07c`. Na árvore dessa release:

- `package/libretro-tic80/libretro-tic80.mk` fixa **b3e158c15997beba019aa02cfad3c7d70caca84e**.
- Esse commit TIC-80 é de **03/09/2019**; `src/tic.h` identifica **0.80.0-dev**. Portanto, não usar a suposição de que o núcleo é necessariamente uma release 0.70.x.
- `configs/recalbox-rpi3_defconfig` inclui `BR2_PACKAGE_LIBRETRO_TIC80=y`.
- O pacote configura `BUILD_LIBRETRO=ON`, `BUILD_PRO=ON`, sem SDL/Sokol nem demos. Isso descreve a compilação do sistema, não exige compra de TIC-80 Pro.
- O readme do sistema especifica `.tic`, `.zip` e `.7z` e aponta `/recalbox/share/roms/tic80`. Entregamos `.tic` sem compressão.
- O código histórico lê separadamente as portas 0 e 1. Os índices TIC são P1 0–7 e P2 8–15.
- No núcleo de 2019, A/B/X/Y do TIC correspondem a **B/A/Y/X do RetroPad**.
- O loader aceita chunk de código 5 e paleta 12 com cabeçalho de quatro bytes; código banco 0 limitado a 64 KiB. A tela lógica é 240×136, 16 cores e a frequência nominal 60 Hz.

Referências primárias:

- [Recalbox: pacote histórico](https://gitlab.com/recalbox/recalbox/-/blob/8ffdef58cf5a555451581c6cf7a8bee33b0ed07c/package/libretro-tic80/libretro-tic80.mk)
- [Recalbox: configuração Pi 3](https://gitlab.com/recalbox/recalbox/-/blob/8ffdef58cf5a555451581c6cf7a8bee33b0ed07c/configs/recalbox-rpi3_defconfig)
- [TIC-80: versão histórica](https://github.com/nesbox/TIC-80/blob/b3e158c15997beba019aa02cfad3c7d70caca84e/src/tic.h)
- [TIC-80: loader legado](https://github.com/nesbox/TIC-80/blob/b3e158c15997beba019aa02cfad3c7d70caca84e/src/tic.c)
- [TIC-80: entrada libretro histórica](https://github.com/nesbox/TIC-80/blob/b3e158c15997beba019aa02cfad3c7d70caca84e/src/system/libretro/tic80_libretro.c)

Uma cópia da declaração do pacote foi preservada em `recalbox61-tic80.mk.txt` para consulta offline. Essas evidências confirmam a distribuição oficial, não uma eventual instalação modificada no cartão.

## O que foi implementado

Cartucho `dist/deshi-dojo.tic`, código original `src/dojo.lua` e MIT em `LICENSE`. Recursos gráficos são primitivas próprias, não sprites KFM/MUGEN. Sem dependência de serviços, BIOS, downloads ou leitura de arquivos durante execução. Sem dados persistentes no cartucho entregue.

APIs TIC utilizadas: `TIC`, `btn`, `cls`, `rect`, `rectb`, `line`, `print`; todas presentes no código histórico e exercitadas no teste de runtime. Sem `BOOT`, `vbank`, bancos extras, compressão de código ou APIs modernas.

Pontuação é uma política separada da detecção de contato. Eventos incluem técnica, distância, zona chudan, qualidade aproximada, atacante/alvo, resultado e frame. A regra atual não é arbitragem oficial. Não há vida sendo reduzida. Avaliação simultânea dos dois lutadores evita priorizar P1 pela ordem das atualizações.

## Runtime de validação e seus limites

O submódulo original `nesbox/3rd-party`, fixado em `62c418b272da3104df4a04a5a280311892d62df5`, não pôde ser obtido: o remoto retornou “Repository not found”. Não desligamos verificação TLS nem substituímos checksums para contornar isso.

Para não interromper a validação das APIs Lua, compilamos os arquivos originais de core, loader, API Lua e entrada libretro do commit histórico **sem alterá-los**, com apenas o interpretador Lua habilitado e dependências públicas fixadas em `tools/runtime-lock.json`:

- Lua 5.3.1: `a1415c0d72053cf6f6f7e68033fa3b7f999ad960`.
- GIF: `1aa11b06d0025eda77b56aec8254130654d4397b`.
- blip-buf: `330226d9b55ecbeea644e17b5e0f096a165ca07e`.

A flag `-fcommon` reproduz o tratamento padrão de símbolos comuns dos compiladores da época, necessário com GCC moderno. O processo não usa o CMake integral de 2019 e não inclui JavaScript, MoonScript, Fennel, Wren ou Squirrel. Não é uma reprodução binária integral do núcleo distribuído no Recalbox. É evidência funcional do loader/API Lua/input históricos em x86-64, com limites explícitos.

As licenças das dependências ficam junto às fontes no cache preparado; o binário de desenvolvimento não é entregue como componente do cartucho nem deve ser copiado ao fliperama.

## Resultados

| Verificação | Resultado | Limite |
|---|---|---|
| Cartucho binário banco 0, código e paleta legados | Passou | Loader histórico compilado localmente |
| Cartucho entregue corresponde ao Lua e SHA-256 | Passou | Geração determinística com Python padrão |
| 14 testes de lógica | Passaram | Lua 5.3.1; desenho substituído por funções vazias neste grupo |
| Carregamento/renderização do cartucho entregue | Passou | 569 frames executados com input sintético e callbacks libretro |
| 16 entradas individuais, 8 por porta | Passou | Entrada injetada pela interface libretro, sem controles físicos |
| Movimento simultâneo e independente P1/P2 | Passou | Núcleo histórico x86-64 |
| Contato, pontuação simultânea, reinício e troca de tela | Passou | Núcleo histórico com telemetria auxiliar só em memória |
| Viewer desktop offline | Passou | 120 frames em Tk/Xvfb; não teste humano no notebook |
| APIs modernas ou cartucho dependente de rede | Não utilizadas | Cartucho e hosts não fazem chamadas de rede durante partidas |
| Windows/macOS | Não testados | Requer runtime nativo apropriado |
| Binário ARM do Recalbox instalado | Não testado | Gabinete/cartão indisponível |
| GPIO, P2 físico, hotkey e monitor LG | Não testados | Verificação presencial necessária |
| 60 fps estáveis no Pi 3 | Não medidos | Não inferir desempenho ARM do resultado x86 |

O teste libretro instrumenta uma segunda cópia do código em memória com `pmem` para ler posições, máscaras e pontos. Essa instrumentação não está no `.tic` distribuído. O cartucho distribuído também é carregado e renderizado sem instrumentação antes desse grupo.

Imagens geradas pelo núcleo: [diagnóstico](diagnostic.png) e [kumite](fight.png). Não são ilustrações conceituais.

## Pendências físicas antes da adoção

Identificar versão/hash reais do núcleo e espaço/cartão, garantir backup verificável, investigar baixa tensão, confirmar quatro ações e direções para ambos os jogadores, testar hotkey de saída, desempenho/temperatura/latência durante 10–15 minutos e regressão dos jogos existentes.

Não instalar novos drivers GPIO, substituir núcleos, atualizar Recalbox, mudar reserva de GPU, aplicar overclock ou formatar o cartão para tentar passar nos testes. Com alimentação inadequada, não prosseguir com gravações.
