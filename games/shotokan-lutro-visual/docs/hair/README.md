# Cabelo no estúdio de personagens

O encaixe e as sobreposições foram corrigidos na revisão v2. Consulte [o diagnóstico e as novas validações](fit-v2.md).

Três cortes aprovados: curto clássico, médio ondulado e crespo curto. Todos disponíveis nos seis corpos, incluindo criança, adolescente e adulto, masculinos e femininos. A opção sem cabelo mantém as bases carecas aprovadas.

No editor local, escolha **Corte de cabelo**, uma paleta ou a **Cor livre**, confira as poses e use **Salvar e levar ao jogo**. Existem 14 opções, incluindo a cor original, preto, castanhos, loiros, ruivo, grisalho, branco e cores fantasia. O seletor livre aceita qualquer RGB hexadecimal. A cor persiste na configuração JSON e nas skins exportadas.

Cada corte tem vistas desenhadas de frente, três quartos, perfil, costas e inclinação. As 1.092 poses dos seis corpos têm anotações de centro craniano, largura, vista, ângulo e sobreposição por mãos/roupa. A preparação fixa o cabelo nessas anotações; a arte do corpo permanece intacta. O mapa e as exceções revisadas são `assets/hair-bindings.json` e `assets/hair-binding-overrides.json`.

As animações que ultrapassam a antiga margem superior recebem espaço transparente acima do corpo. Os quadros empacotados guardam a origem lógica, inclusive coordenadas negativas. Não há redução do personagem para acomodar cabelo. Os testes verificam que os pixels do corpo e a escala são idênticos à base em todas as alturas e portes.

A recoloração usa exclusivamente o material isolado do cabelo. As rampas preservam contornos, mechas e diferenças entre sombra e luz, inclusive em branco e preto. Pele, faixa, gi e demais pixels ficam protegidos. As mãos e mangas que cruzam a cabeça mantêm sua sobreposição. As faixas continuam sendo recursos independentes compartilhados entre skins com a mesma geometria.

Tudo é compilado no computador de desenvolvimento, tanto nos 92 quadros básicos quanto nos 90 quadros de especiais, queda e apresentação. O cartucho usa os mesmos sprites prontos do HTML; nenhuma nova dependência, filtro, shader ou modelo 3D foi adicionado ao runtime. O cadastro existente permanece intacto: os cabelos aparecem nos personagens exportados depois de escolhidos no editor.

Arte: imagegen integrado. Os três pilotos aprovados estão em `assets/source/hair-pilot-v1/`, com prompts. As folhas de registro e os 18 recortes das vistas estão em `assets/source/hair-v1/`, com seu conjunto de prompts. Os manequins cianos das folhas servem apenas para registro; cabeça e fundo são removidos pelo importador de materiais. Não são modelos 3D.

Risco de regressão: alto, por envolver compilação, cache, exportação e seleção dos personagens. Validação:

- `tests/hair_assets.py`: 3.276 encaixes; 29.484 combinações de altura/porte; 45.864 verificações de paleta; transparência binária, proteção dos pixels do corpo, piso e roundtrip de 92 quadros pelo empacotador.
- `tests/hair_creator.py` + `tests/hair_editor.cjs`: 18 previews reais, cor livre salva e reaberta, seis corpos exportados, mesmos dados no HTML/Lutro, saudações, saltos, nidan e todos os quadros especiais nos dois ports. Memória retida das seleções básicas: 103.383.760 bytes, abaixo do orçamento de 128 MiB.
- `tests/hair_live.cjs`: editor real no localhost, branco, troca de corpo preservando o corte, opção careca e cadastro sem alterações.
- `tests/character_creator.py`: CRUD/exportação anterior, pele retinta em 90 quadros, combate, CPU, seleção F2 e cache.
- `tests/browser.cjs`: 13 grupos de regressão do combate; `tests/specials.cjs`: comandos e finalizações.
- `tests/package.py`, `tests/editor_rebuild_cache.py`, compilação Python e verificação do diff.

As pranchas de revisão mostram todos os encaixes. Os três `*-runtime.gif` vêm do canvas real de um HTML exportado pelo teste isolado, que cadastra seis exemplos sem alterar o cadastro do desenvolvedor. Não há interpolação ou animação simulada; o empacotador verifica os pixels de cada quadro do GIF contra a captura correspondente.

Raspberry Pi 3/Recalbox e joysticks físicos não foram executados. A validação local da API histórica e do orçamento não substitui essa execução física. O runtime mantém seu limite existente de imagens retidas; grandes elencos precisam respeitar o orçamento na exportação e seleção.
