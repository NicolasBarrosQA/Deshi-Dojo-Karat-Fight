# Tom de pele — estúdio de desenvolvimento

Abra `http://localhost:8769/editor`. A personalização pertence à preparação dos personagens, antes da produção. O cartucho e o HTML recebem PNGs prontos; não aplicam filtro, shader ou cálculo de cor durante a luta.

Há 11 paletas de pele e a opção de preservar a arte original: porcelana, clara neutra, clara dourada, clara oliva, média neutra, média dourada, média oliva, morena bronze, castanha, escura e retinta. Cada paleta tem sete pontos de sombra/luz, com interpolação contínua; contornos escuros, transparência, resolução e posição dos pixels permanecem preservados. O karategi e as faixas são materiais separados.

1. Escolha um personagem salvo ou crie um novo.
2. Se desejar outra skin do mesmo personagem, use **Duplicar / criar skin**. O cadastro original permanece separado.
3. Escolha a paleta e habilite **Comparar com a arte original**. Confira poses, movimentos e as duas direções.
4. Use **Salvar e levar ao jogo**. O sistema prepara as 92 poses básicas, os 72 quadros de especiais/queda e o retrato; **Exportar HTML e Lutro** gera a entrega.

Na versão de produção, os jogadores escolhem personagens/skins preparados e a faixa. O joystick não edita tom de pele, corpo, rosto ou cabelo. As ferramentas de corpo do HTML aparecem apenas com `?developer=1` (ou no modo de captura de testes); o editor fica em sua rota local de desenvolvimento.

As faixas e a geometria são compartilhadas entre skins equivalentes. Só as variantes salvas são incluídas no jogo: a biblioteca de paletas do editor não é carregada pelo cartucho. Os arquivos gerados têm chaves de aparência e assinaturas das fontes; alterar uma paleta ou um sprite invalida as prévias antigas. Os IDs históricos `clara`, `media` e `escura` continuam válidos.

Verificações: `tests/skin_palettes.py` cobre 984 posições e 11.808 combinações de pose/tom; `tests/appearance.py` reconstrói as seis bases, os espelhos e as oito faixas; `tests/skin_editor.cjs` verifica amostras, comparação, duplicação e a separação da interface de produção. `tests/character_creator.py` testa cadastro, reabertura, exportação, combate real e a cor exata dos 72 quadros de especiais de uma skin retinta em checkout temporário, sem editar os personagens do projeto.

`guards.png` e `jump-descent.png` mostram os pixels do jogo preparados pelo mesmo material utilizado no exportador. `editor.png` é uma captura do editor real. Os testes de cache conferem os recursos exatos da dupla e o orçamento histórico de 128 MiB. Raspberry Pi 3/Recalbox 6.1 físico continua sem medição nesta máquina.

Preparação no computador de desenvolvimento requer Python, Pillow e NumPy. Nenhuma dessas dependências vai no cartucho.
