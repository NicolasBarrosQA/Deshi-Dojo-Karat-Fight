# Personalização v07 — 11/10/2026

## Jogar e testar as bases

Na raiz: `python scripts/play_web.py`. Escolha corpo e faixa de P1 e P2 abaixo da luta. F2 abre o mesmo recurso no cartucho: direções escolhem a linha, soco/chute altera o valor, defesa fecha. As quatro primeiras linhas escolhem o modo. Enter/revanche e mudanças de dificuldade preservam a aparência. Atualizações continuam por `git pull` e F5, sem dependências novas para jogar e sem chamadas externas durante a partida.

Adulto, adolescente e criança têm **92 poses cada**, na ordem dos IDs originais, incluindo as poses arquivadas. As 92 poses do adulto mantem os pixels originais e sua escala nativa, inclusive no salto. Medir a largura do cabelo para reduzir todo o corpo causava encolhimento do tronco e foi removido. Adolescente e criança foram redesenhados com a ferramenta integrada `image_gen`, usando as folhas adultas como referência de poses; não são redimensionamentos do adulto. A revisão 2 substitui as primeiras folhas de baixa resolução, que ficaram borradas. Agora cada base tem sete folhas em `assets/source/characters-v2`, com no máximo 16 poses por folha. O importador exige altura mediana de origem de pelo menos 160 pixels, proíbe ampliação e reduz uma única vez com nearest-neighbor. Nas três bases, a escala aérea usa a cabeça no tamanho final em pixels como referência; a altura encurtada pelos joelhos dobrados não deve aumentar o personagem. A anatomia e a exatidão Shotokan das ilustrações continuam sujeitas à revisão do instrutor.

As opções são branca, amarela, vermelha, laranja, verde, roxa, marrom e preta. `belt_order` em `assets/characters.json` é uma ordenação editável do dojo, não uma sequência universal de graduação. A CPU mantém seus três perfis de comportamento; sua faixa pode ser qualquer uma dessas opções. As cores históricas dos perfis continuam na barra de energia, separadas da faixa desenhada no karateca.

## Cadastro de aluno

O cadastro é independente da máquina de combate e do manifesto de imagens. Adicione em `assets/characters.json`, dentro de `students`, por exemplo:

```json
"aluno-exemplo": {
  "name": "ALUNO EXEMPLO",
  "body": "child",
  "face": "default",
  "hair": "default",
  "belt": "amarela"
}
```

Inicialização Lua: `Scene.student(1, 'aluno-exemplo')`. Para uma alteração pontual: `Scene.character(2, {body='teen', belt='verde'})`. `name` é o nome do aluno e não muda quando seu corpo é selecionado. A fonte histórica mostra ASCII; use um nome de exibição sem acentos. O builder recompõe `character_data.lua` a partir dos JSONs. O servidor observa cadastro, manifesto, módulos e PNGs; F5 incorpora as alterações. Arquivos Lua gerados ficam fora da assinatura de observação, evitando reconstruções contínuas.

## Camadas e encaixes

`characters.lua` desenha **corpo → faixa → rosto → cabelo → primeiro plano**. `character-assets.json` descreve cada parte; `character-masks.json` registra regiões editáveis por base e pose. Cada quadro contém `sx`, `sy`, `w`, `h` no atlas compacto e `x`, `y` na célula lógica 224×144. Os pixels das partes padrão são uma partição disjunta da ilustração original. O primeiro plano repõe gi/braços sobre a região da cabeça. Se uma mão encobrir rosto/cabelo em uma nova identidade, acrescente retângulos `foreground: [[x0,y0,x1,y1], ...]` à máscara da pose e confira a oclusão. As máscaras iniciais são derivadas por regiões e pigmentos; devem ser refinadas visualmente ao cadastrar outra identidade, especialmente nas defesas cruzadas e reações.

Os atlases esquerdos são espelhados por quadro, não como folha inteira. O encaixe usa `224-x-w`, conservando o pivô durante o espelhamento. Nas novas bases, o último pixel dos pés é a linha 142 da célula; o adulto preserva sua variação histórica de 1–2 pixels. A posição vertical é subtraída da altura do salto; as poses aéreas mantêm seus IDs e a física existente.

A faixa usa uma máscara binária por pixel em `assets/character-belt-{body}-mask.png`, com cintura, nó e pontas. O antigo retângulo de busca não determina mais os pixels coloridos. `character-belt-overrides.json` registra contornos de inclusão/exclusão para partes separadas por oclusão; os contornos selecionam somente pixels existentes, sem redesenhar o sprite. `tools/review_belts.py` mostra a seleção em amarelo no tamanho nativo ampliado por fator inteiro. Para aplicar correções aos contornos, use `python tools/import_characters.py --repack --refresh-belt-masks`; para editar diretamente a máscara já revista, use apenas `--repack`. Os testes exigem que cada troca de paleta altere exatamente os pixels dessa máscara, sem alterar gi, pele, cabelo ou silhueta.

Para **adicionar rosto ou cabelo sem redesenhar corpos/animações**, produza arte com as vistas necessárias (lateral, costas, defesa etc.) em uma folha transparente. Crie um mapa com 92 referências às vistas; várias poses podem reutilizar a mesma vista e receber apenas offsets:

```json
{
  "views": {"right": [0, 0, 24, 24], "rear": [24, 0, 24, 24]},
  "poses": [{"view": "right", "dx": 0, "dy": 0}]
}
```

O exemplo de `poses` acima é abreviado: o importador exige exatamente 92 entradas. Use a vista traseira nas poses de costas; para ocultar o rosto quando não é visível, use {"view": null}. Não repita uma face lateral em todas as orientações. Ajuste `dx`/`dy` quando necessário, sem deformar a arte. Execute, dentro da pasta do jogo:

```bash
python tools/import_identity.py --body child --layer hair --id cabelo-curto --sheet assets/source/cabelo-curto.png --mapping assets/cabelo-curto.json
python tools/build.py
```

Cadastre `hair: "cabelo-curto"` no aluno. O importador altera apenas o manifesto e os atlases dessa parte. As vistas podem ser reutilizadas entre poses e alunos compatíveis; cada base tem encaixes próprios. Rosto/cabelo substituem suas camadas padrão, em vez de sobrepor uma cabeça inteira ao sprite original. Revise máscaras e primeiro plano para qualquer mudança de silhueta. Não há fotos ou alunos reais nesta entrega.

Reimportar as três bases: `python tools/import_characters.py`. Ele preserva variantes de rosto/cabelo já registradas; se a arte corporal/encaixes mudar, reimporte essas identidades para realinhar. Pillow é ferramenta de desenvolvimento/importação e testes, não dependência para executar `play_web.py`. Alterações de RGB de faixa exigem reimportação; apenas reordenar faixas ou cadastrar aluno exige o builder padrão.

## Motor histórico e memória

São usados somente PNG, `newImage`, `newQuad`, `draw` e coordenadas inteiras. Todos os assets finais têm alpha binário 0/255; a importação usa limiar 128 e limpa RGB invisível. As faixas são paletas pré-empacotadas de uma máscara comum, sem tint, shaders, transparência parcial ou escala de LÖVE moderno. As fontes históricas verificadas são [graphics.c](https://github.com/libretro/libretro-lutro/blob/a031f95394440022a561ce593d578474ac119c05/graphics.c) e [image.c](https://github.com/libretro/libretro-lutro/blob/a031f95394440022a561ce593d578474ac119c05/image.c).

Uma instância selecionada ocupa aproximadamente 9–17 MiB de pixels para as duas direções e cinco camadas, com partes compartilhadas deduplicadas. O navegador decodifica somente opções ativas; as demais ficam como PNGs comprimidos no HTML offline. A seleção carrega as novas partes de forma assíncrona. O HTML completo após as correções de salto/faixa tem cerca de 15 MB; isso inclui os três corpos e paletas, mas não combinações pré-renderizadas por aluno.

**Limitação descoberta no núcleo de 2019:** `ImageData.__gc` é vazio. Descartar uma imagem e carregá-la de novo pode manter os buffers antigos alocados. No nativo, portanto, somente partes visitadas são carregadas e ficam em um cache persistente, sem recarregar o mesmo caminho. Todas as bases/faixas padrão visitadas somam 68.021.856 bytes (64,9 MiB). Há um limite explícito de **80 MiB** para novos assets; não é uma medição da RAM total do jogo. Catálogos maiores devem reiniciar o cartucho ou ser repartidos antes desse limite. No navegador os canvases inativos são removidos. A lógica de cache foi simulada; seu consumo real no Lutro/Raspberry Pi ainda não foi medido.

## Colisões e defesas

As três aparências compartilham a máquina de combate, tempos, alcance, dano, combos e **volumes de combate normalizados do adulto original**. A barreira corporal permanece 88 pixels. Esta decisão preserva os combates e evita tornar a criança quase intocável ou reduzir seu alcance por uma escolha visual. Consequência: o volume virtual de cabeça/tronco pode ultrapassar a silhueta de uma criança; o modo de colisões mostra esses volumes. Não se afirma que a colisão acompanha anatomicamente cada corpo. Uma futura regra por idade/altura deve tratar alcance e contatos conjuntamente, com balanceamento e revisão do dojo.

Guarda neutra (`kamae`) cobre jodan/chudan; gedan exige defesa baixa. Durante a preparação da primeira defesa não há cobertura. Ao trocar uma defesa já pronta por outra, a cobertura anterior continua; a nova zona e a recepção precisa só começam depois de `windup`. Soltar a guarda, atacar, ficar atordoado ou saltar invalida a cobertura. Os contatos têm `defense` (a defesa que realmente cobriu) e `defenseReason`, independentes da nova solicitação. A interface do navegador mostra zonas cobertas e motivo do último contato; o cartucho mostra defesa efetiva/linha na mensagem.

## Validação e pendências

- Importação mecânica: 276 poses, 2.208 combinações pose/faixa, alpha binário, reconstrução, âncoras e espelhamento exato. Cabeça no salto de adolescente/criança dentro de 8% da referência em pé; todas as 92 poses adultas preservadas pixel a pixel.
- Chrome no Windows offline: seletores, todas as poses, duas bases diferentes, 200 ticks de colisão, aparência independente da CPU/reset, zero chamadas externas/erros.
- Defesa: 150 casos de transição/zona/jogador, soco alto por teclado bloqueado sem perder energia e dois contatos reais durante kamae→gedan, cobrindo ambos os lados e registrando `kamae` sem recepção prematura.
- Cache histórico simulado: todas as bases/faixas revisitadas não criam imagens adicionais e permanecem abaixo do limite.
- Regressões existentes: teclado/combate (13 verificações), CPU (6 verificações, incluindo partidas completas de pressão só com soco), integridade LF/CRLF e reconstrução automática por mudanças de cadastro.
- HTML e `.lutro` foram empacotados; o builder padrão não gera ZIPs.

Comandos: `python tests/personalization.py`, `node tests/personalization.cjs`, `node tests/browser.cjs`, `node tests/cpu_browser.cjs`, `python tests/windows_checkout.py`, `python tests/server_rebuild.py`. Testes gráficos usam Pillow/Playwright apenas no ambiente de desenvolvimento. Os scripts aceitam `DOJO_CHROMIUM` e têm caminho padrão de Chrome no Windows.

**Não validado nesta entrega:** execução do cartucho no núcleo histórico, paridade nativo/browser, ARM, Recalbox do gabinete, GPIO, gamepads físicos, desempenho/RAM/FPS no Pi 3 e baixa tensão. O `.so` Linux anterior não existe neste checkout Windows. A falha anterior `guard-kamae-p2`/`diffbbox (60,67,325,196)` não é reproduzível aqui: não recebemos as alterações locais nem o núcleo do workspace anterior. O teste `raster.py` permanece exigindo igualdade pixel a pixel, sem tolerância ampliada ou remoção de casos; somente os novos módulos foram incluídos nas fixtures. Essa falha segue pendente até executar o núcleo histórico. Nenhum arquivo/configuração do gabinete foi acessado, e IKEMEN/TIC-80 permanecem intactos.

## Arte e proveniência

O editor e a geração antecipada de aparências acrescentados depois desta análise estão descritos em [Criador de personagens](CRIADOR-DE-PERSONAGENS.md). Os números de recursos das camadas padrão abaixo não incluem os novos perfis compactados de aparência.

Ferramenta usada: `image_gen` integrada. Fontes finais nas pastas `assets/source/characters-v2/child` e `teen`; ordem das sete folhas em `assets/character-source-layout.json`. O adulto usa as fontes/poses existentes. Cada geração referencia a folha adulta da sequência e o novo modelo da idade, mantendo os gestos/IDs, gi branco, faixa preta, pés descalços e contornos arcade definidos. As antigas folhas únicas foram rejeitadas por baixa nitidez e permanecem somente como histórico. Python faz normalização de alpha, extração dos componentes completos, redução nearest-neighbor, separação por máscaras, aplicação mecânica de paleta e empacotamento; não desenha corpos.

Evidências: `personalization-results.json`, `personalization-browser-results.json`, `personalization-browser.png`, `character-*-atlas.png`, `character-art-v2-native-review.png`, `character-art-v2-zoom-review.png` e `assets/character-import.json`. Prompts exatos e caminhos da revisão atual: `assets/character-provenance-v2.json`; a proveniência anterior fica em `assets/character-provenance.json`.

A reproducao no navegador comeca em meia velocidade para acompanhar as fases dos golpes. O botao Velocidade alterna entre 0.5x, 0.25x e 1x; demonstracao e treino reiniciam em 0.5x. Comandos, tempos em ticks, colisoes e regras de defesa permanecem iguais. O cartucho Lutro mantem seu ritmo original.

Com o criador e os tres perfis demonstrativos, o HTML offline atual tem aproximadamente 28,7 MB e o cartucho 21,0 MB. PNGs comprimidos ficam no pacote; apenas os visuais escolhidos sao decodificados. O cache simulado de nove cadastros mais um personagem criado pelo editor reteve 35.635.200 bytes (34,0 MiB), sem alocacoes adicionais ao revisitar os mesmos perfis. Esses numeros nao medem a RAM total no Raspberry Pi.
