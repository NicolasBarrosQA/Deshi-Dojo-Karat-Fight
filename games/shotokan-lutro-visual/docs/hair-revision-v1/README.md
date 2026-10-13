# Revisão da direção de arte

O lote de 20 cabelos novos e seis barbas foi reprovado visualmente pelo usuário. Ele foi retirado da seleção do editor com `available: false`, preservando fontes, IDs e compatibilidade de personagens já salvos. Os três cabelos aprovados anteriormente continuam oferecidos. O importador preserva a retirada; importar novamente não publica as artes automaticamente.

A amostra de rabo baixo é um estudo **não aprovado**, com apenas uma vista de três quartos. Foi editada a partir da vista do curto clássico aprovado para manter a linguagem gráfica e a referência anatômica. Não foi adicionada ao catálogo nem usada nos personagens de produção.

`01-rabo-baixo-aplicado.png` mostra os sprites neutros originais de criança e adulta, com a amostra em guarda. A parte de cima está ampliada 2× e o detalhe da cabeça 4×, ambos por nearest-neighbor. A composição usa o mesmo posicionamento e as mesmas máscaras do exportador; não redesenha o corpo. A geometria fora da cobertura de cabelo foi comparada pixel a pixel com os originais. Este estudo não representa validação das demais poses.

Gere novamente a comparação com `tools/preview_hair_revision.py`. A fonte está em `assets/source/hair-revision-v1`. O teste `tests/hair_catalog_visibility.py` verifica a retirada do lote e a preservação de configurações existentes. A avaliação visual no tamanho do jogo deve orientar a próxima revisão do catálogo.
