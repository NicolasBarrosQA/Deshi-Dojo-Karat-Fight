# Cabelos cotidianos e barbas

**Estado atual: lote reprovado visualmente pelo usuário e retirado das opções do editor.** Somente os três cortes aprovados anteriormente continuam oferecidos. As fontes e os resultados abaixo foram preservados para revisão; os testes verificam geometria e funcionamento, não aprovação estética. Importar novamente as fontes mantém essa retirada.

Entrega ajustada ao pedido final: **10 cabelos masculinos novos, 10 femininos e seis estilos de barba**. Os três cabelos aprovados anteriormente continuam disponíveis: 23 cabelos no total.

Masculinos novos: buzz, crew cut, Caesar, French crop, risca lateral, repartido ao meio, franja lateral, cacheado curto, cacheado médio e afro arredondado. Femininos: pixie curto e longo, chanel reto, com franja, ondulado e cacheado, coque de bailarina, rabo alto, rabo baixo e coque trançado. Barbas: curta, cheia, quadrada, cavanhaque, Van Dyke e bigode.

As coleções ajudam a encontrar os estilos; não restringem o corpo que pode usá-los. Todos foram preparados para as seis bases aprovadas. Cabelos compridos desta seleção ficam presos ou compactos para treinamento de karatê. Nenhum estilo adicional foi criado contando apenas uma mudança de cor.

## Editor e exportação

Abra `http://localhost:8769/editor` e atualize a página. Há miniaturas, busca por nome, filtro masculino/feminino, seleção de barba e cores independentes. Cabelo e barba aceitam as 14 paletas existentes e qualquer cor hexadecimal. Os personagens salvos, nomes, IDs, faixas e tons de pele foram preservados.

As imagens são preparadas no computador do desenvolvedor e incorporadas aos atlas finais. O HTML e o Lutro continuam recebendo sprites prontos, sem geração de imagens, filtros, personalização ou serviços externos durante a luta. O catálogo de fontes não é carregado inteiro pelo Raspberry Pi: somente os personagens escolhidos para o elenco são exportados.

## Encaixe e qualidade

Cada corte tem uma arte própria em seis vistas. O registro do crânio usado pelos três estilos aprovados foi mantido. A barba tem uma máscara de mandíbula própria, derivada dos sprites neutros originais. Mãos, mangas e contornos permanecem na frente; as máscaras não dependem da cor de pele selecionada. Dois pontos adicionais da mão na defesa alta do adulto foram revisados para os novos cortes curtos.

As pranchas `hair-guard-*`, `hair-raised-hand-*`, `hair-floor-*` e suas equivalentes de barba mostram o compositor usado na exportação. Cada estilo também tem uma prancha individual com os seis corpos e poses de guarda, defesa alta, giro, salto, reverência e queda. Franjas e mechas visíveis ficam na frente da barba, inclusive quando as duas têm cores diferentes.

## Validação

- `tests/hair_catalog.py`: 31.668 combinações de estilo, corpo e pose; 285.012 combinações de altura/porte; 2.610 verificações de materiais e cores. Zero erros. Todas as 182 poses de cada corpo foram verificadas.
- `tests/hair_fit_regression.py`: seis âncoras anatômicas independentes, 1.656 verificações de cobertura do crânio em todos os tons de pele, 69 verificações da mão na defesa alta com cabelos e 18 com barbas.
- `tests/hair_beard_layers.py`: todos os 138 pares de cabelo/barba, em oito poses representativas e nos seis corpos. As 6.624 combinações incluem 3.682 sobreposições reais, verificadas com cabelo branco e barba preta para revelar erros de ordem das camadas. Zero erros.
- `tests/hair_creator.py`: edição real, filtros e busca, todas as barbas em prévia, cor livre salva/reaberta, seis corpos exportados, todos os quadros dos especiais, duas orientações, salto, nidan e cumprimento no HTML offline. O mesmo elenco foi confirmado no cartucho Lutro. O teste de superfícies nativas com 12 personagens reteve 103.671.792 bytes, abaixo do limite de 128 MiB.
- `tests/hair_live.cjs`: editor real da porta 8769, troca de corpo, opção careca, revisão de cache e comparação dos pixels dos dedos no atlas final do buzz cut. Nenhuma escrita no elenco.
- `tests/package.py`: módulos, dimensões, caminhos portáveis e hashes do cartucho aprovados. O elenco original mantém os mesmos hashes de HTML e Lutro.

Os GIFs em `../hair/*-runtime.gif` vêm da execução real do HTML exportado em um projeto temporário; 119 capturas por sequência. `tools/pack_hair_gifs.py` compara todos os pixels decodificados com as capturas. Não são animações simuladas.

Não foi executado um Raspberry Pi físico nesta entrega. A verificação de superfícies nativas mede a retenção das imagens básicas do elenco de teste; não é uma medição de FPS no aparelho.

## Reprodução

Use o Python de autoria com Pillow e NumPy. Prepare máscaras com `tools/prepare_hair_bindings.py`, importe as artes com `tools/import_hair_catalog.py` e gere as pranchas com `tools/review_hair_catalog.py`. Execute os testes acima e `tools/build.py`. As fontes e a proveniência ficam em `assets/source/hair-catalog-v1`; as artes excedentes do pedido inicial foram arquivadas em `.runtime/hair-catalog-extra` fora do catálogo.
