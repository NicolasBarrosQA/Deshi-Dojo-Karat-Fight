# Poses originais 2D — primeiro conjunto

Direcao confirmada pelo usuario: desenho 2D a partir das seis bases aprovadas. Nenhum modelo 3D participa desta entrega.

Foram produzidas seis pranchas originais com a ferramenta integrada image_gen: guarda, soco reto e chute frontal, totalizando 18 poses. Fontes transparentes e prompts exatos estao em assets/source/avatar-poses-2d-v1. As bases originais aprovadas foram preservadas.

O script tools/present_avatar_poses_2d.py extrai os tres personagens por componentes conectados, evitando cortar pes quando ultrapassam a divisao das colunas. Mantem uma escala unica por corpo nas tres amostras, piso em y=143 e canvas 224x144. As pranchas de revisao em alta resolucao usam tamanho de apresentacao; somente estudo-resolucao-nativa.png representa as alturas propostas para o jogo (93/111/129 pixels). A reducao usa LANCZOS e alpha binario; a ampliacao de exibicao usa nearest-neighbor.

Verificacao: 18 recortes e 18 amostras nativas gerados sem exceder o canvas; revisao visual das duas pranchas corrigidas, incluindo maos, pes, partes indevidamente recortadas e silhuetas. Risco baixo: ferramenta isolada de apresentacao, sem mudanca no motor, no criador, no cartucho ou no HTML. Nao houve teste fisico em Raspberry Pi 3/Recalbox 6.1. Cada celula RGBA de 224x144 ocupa 129024 bytes descomprimidos; isso nao mede a memoria total ou o desempenho do jogo.

Este conjunto ainda nao e uma animacao completa nem substitui os sprites em uso. Faltam preparacao, recolhimento, intermediarias, deslocamentos, defesas, saltos, quedas e especiais. A fidelidade tecnica do soco (lado do quadril/braco/perna) precisa ser consolidada com as transicoes antes de usar como demonstracao didatica. A faixa branca esta desenhada nas fontes; mascaras exclusivas de cintura, no e duas pontas precisam ser preparadas para personalizacao. Rostos e cabelos continuam ausentes, conforme as bases aprovadas.

Arquivos de revisao:

- poses-2d-seis-corpos.png: primeiro conjunto em alta resolucao.
- estudo-resolucao-nativa.png: os mesmos desenhos reduzidos e ampliados 2x sem suavizacao.
- manifest.json: hashes das fontes, escalas e dimensoes.
- pastas por corpo: recortes individuais e amostras 224x144.
