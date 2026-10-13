# Reconstrução completa dos cabelos e encaixes

O usuário rejeitou **todos os cabelos e encaixes**, masculinos e femininos, novos e antigos. Nenhum dos três cortes iniciais serve como direção aprovada. Todos os cabelos e barbas existentes foram retirados das opções do editor. As fontes foram preservadas, sem alterar personagens salvos ou as seis bases carecas aprovadas.

## Problema encontrado

O posicionamento anterior usava o maior círculo inscrito na pele visível para estimar o crânio. A largura resultante do adulto varia de 14 a 22 pixels entre poses. Essa medida depende da região visível e não define, sozinha, o crânio completo, a linha de cabelo, a têmpora ou a nuca. As imagens de cabelo eram desenhadas sobre cabeças genéricas e reduzidas para essa medida. Os testes antigos verificavam limites, cores e poucos pontos de contato; não validavam a forma anatômica em todas as poses nem a direção artística.

`old-skin-radius-audit.png` mostra a medida antiga sobre os sprites originais, em guarda, giro, salto e queda. Ela foi preservada para diagnóstico, não adotada como encaixe da reconstrução.

## Estudos atuais

- Referências extraídas das seis cabeças reais, mantendo o desenho original e sua grade de pixels.
- Um estudo de corte masculino curto e um de chanel feminino, cada um desenhado sobre as seis cabeças reais em guarda.
- Material verde apenas como identificação interna da camada de cabelo. A extração preserva as cinco tonalidades declaradas, incluindo luzes; o resultado de avaliação é castanho, com corpo e pele originais.
- A camada é posicionada nas coordenadas nativas da referência. Não usa o raio antigo, um molde de cabeça genérica nem redimensionamento para o componente de pele visível.
- `native-six-head-studies.png` mostra 12 amostras: dois cortes sobre os seis corpos. Os detalhes são ampliados 3× sem suavização. `native-family-checks.json` registra a preservação dos pixels originais fora do cabelo e a cobertura da região superior do crânio em guarda.

**Os dois cortes desta reconstrução foram aprovados visualmente pelo usuário em 12/10/2026 e integrados ao editor.** A aprovação artística corresponde à arte apresentada em `native-six-head-studies.png`: corte masculino curto e chanel feminino, sobre as seis bases originais. Os cabelos antigos continuam rejeitados. A integração dos movimentos foi posteriormente implementada e validada pelos testes abaixo.

A checagem independente do topo real do crânio encontrou um pixel exposto no estudo curto sobre a adulta. O preparo das camadas finais sela pequenas lacunas de amostragem na coroa com o material adjacente, sem alterar rosto, corpo ou desenho do corte. `tests/native_head_family_guard.py` agora verifica as camadas finais: passou nas 12 combinações de guarda. A checagem anterior por faixa fixa não abrangia o topo do adolescente e foi substituída por três linhas a partir do topo de pele de cada cabeça.

## Integração dos movimentos

- Vistas de frente e de costas dos mesmos cortes, desenhadas sobre as cabeças originais. As vistas traseiras foram geradas com a ferramenta integrada ImageGen, usando as referências reais e os cortes aprovados. Somente a camada marcada como cabelo foi importada; corpos redesenhados pela geração não entram no jogo.
- Registro contra o contorno real da coroa e têmpora de cada pose. Os centros anteriores apenas iniciam a busca; seu raio de pele não determina o tamanho do cabelo. Ajustes de escala são limitados a 0,9–1,1 da vista corporal de referência e gravados explicitamente, junto com posição e ângulo, em `native-pose-registration.json`.
- Máscaras de mãos, braços e gi derivadas da arte original permanecem à frente do cabelo. A máscara independe da cor escolhida para a pele. Halos de fundo marcados em verde são excluídos pela região anatômica e pelo componente conectado de cabelo.
- 2.184 camadas prontas: dois cortes × seis corpos × 182 poses. As 12 folhas `*-all-poses.png` foram conferidas visualmente. Cor, posição e sobreposição são preparadas no computador do desenvolvedor; o jogo recebe sprites finais, sem novo cálculo de cabelo durante a luta.
- Os 23 cortes anteriores e seis barbas permanecem fora do catálogo oferecido. Configurações antigas continuam legíveis; personagens, nomes e faixas não foram sobrescritos.

## Validação e limites

Risco: médio, por afetar o compilador visual compartilhado. Pontos de regressão: sobreposição de braços, cor de pele, cores claras de cabelo, orientação esquerda/direita, extensão do atlas e exportação.

Passaram: `native_hair_material.py`, `native_head_family_guard.py`, `native_hair_poses.py` (2.184 poses, quatro paletas e três proporções), `hair_fit_regression.py` (inclui a defesa do relato), `hair_catalog_visibility.py`, `hair_live.cjs` (editor real, sem salvar no elenco) e `native_hair_creator.py` (12 aparências em exportação isolada, jogo HTML offline, todos os quadros especiais nos dois jogadores, saltos, nidan e ushiro executados).

`native-runtime-tests.json` registra resultados do navegador. HTML e Lutro foram gerados a partir do mesmo elenco de teste. `runtime-*.gif` contém quadros capturados do canvas real do jogo; `runtime-capture-provenance.json` registra hashes dos PNGs de origem. GIFs individuais para os seis corpos mostram os dois cortes em salto, nidan e ushiro.

A contabilidade nativa dos atlas básicos para um elenco de seis personagens foi de 52.453.472 bytes no curto e 52.682.400 no chanel. Incluindo todos os especiais, reverência e toque de mãos nas duas orientações, os totais foram 98.248.792 e 98.720.448 bytes (aproximadamente 93,7 e 94,1 MiB), abaixo do limite existente de 128 MiB. A verificação fica em `native-full-roster-budget.json`. O teste extremo com dezoito personagens atingiu o limite existente de retenção: o limite e a proteção do Lutro histórico foram preservados. Esses números medem superfícies de sprites; não são a memória total do processo. Não foi executado teste físico em Raspberry Pi.

As bases carecas do elenco real continuam intactas. A recompilação de seu HTML e cartucho produziu os mesmos hashes anteriores. Para levar os cortes ao fliperama, selecione-os no editor, personalize a cor e exporte o personagem normalmente. A biblioteca de cabelo não é carregada inteira no jogo.

A ampliação do catálogo depende de acertar a direção visual no tamanho real do jogo e o movimento dos dois estudos. Não gerar novamente um lote de cortes sobre o encaixe antigo. Manter preparo offline, Lua 5.1, arquitetura do combate e exportação de sprites prontos para Lutro/HTML.

## Reprodução

`tools/head_reference_studies.py` e `prepare_native_hair_rear.py` extraem referências reais. `tools/bake_native_hair.py` registra os crânios e grava os atlas de camadas e o manifesto. `--reuse-registration` permite reaproveitar os encaixes conferidos quando só a extração do material mudou. `tools/register_native_hair.py` publica os dois cortes aprovados e suas miniaturas. `tools/pack_native_hair_gifs.py` empacota exclusivamente os PNGs capturados pelo teste do jogo.
