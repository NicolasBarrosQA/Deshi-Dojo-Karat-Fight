# Criador de personagens

No notebook, abra um terminal na pasta do repositório e execute:

```powershell
python scripts/play_web.py
```

Abra **http://localhost:8000/editor**. Se a porta estiver ocupada, use `--port 8001` e abra esse endereço. O editor e o jogo funcionam localmente, sem contas ou serviços externos. A preparação visual usa Pillow no notebook; o servidor procura a instalação do Python em uso e o runtime local do Codex. Se faltar, a mensagem orienta a instalação gratuita `python -m pip install Pillow`. Nem HTML offline nem Lutro precisam de Python/Pillow para jogar.

1. Clique em **Novo personagem**.
2. Preencha nome e, se quiser, apelido. O identificador precisa ser único; depois de salvar, ele fica fixo.
3. Escolha adulto, adolescente ou criança, faixa, pele e cor do cabelo. Para adultos, **Rosto e cabelo** oferece quatro identidades desenhadas com miniaturas, além do personagem original. Os conjuntos novos incluem vistas para giros, inclinações e quedas; seus rostos e cabelos ainda não são combináveis separadamente.
4. Ajuste altura (94%, 100% ou 104%) e porte (leve, médio, forte). São ajustes visuais limitados, aplicados a todas as poses; não alteram a física ou o alcance arcade.
5. Confira poses individuais, socos, chutes e defesas. A prévia é recomposta automaticamente após cada alteração. Você pode pausar e trocar a direção.
6. Clique em **Salvar e levar ao jogo**. O servidor persiste o JSON e reconstrói HTML e cartucho.
7. Clique em **Executar jogo**, escolha o personagem em P1 ou P2 / CPU e lute. Atualize uma janela do jogo que já estava aberta.

Para editar, escolha um personagem na lista, altere os campos e salve. **Baixar configuração JSON** cria uma cópia portátil; **Importar configuração** valida e abre o cadastro, que só entra no jogo após salvar. A importação exige que os recursos artísticos indicados existam nesse projeto.

O botão **Exportar HTML e Lutro** reconstrói o jogo e baixa o cartucho. O HTML completo fica em `games/shotokan-lutro-visual/dist/deshi-dojo-visual.html`; ele pode ser copiado e aberto offline. O cartucho fica ao lado, em `deshi-dojo-visual.lutro`. No Lutro, abra o menu F2/Select, navegue até **P1 ALUNO** ou **P2 ALUNO** e pressione soco para alternar; retratos dos escolhidos aparecem no menu. A dificuldade da CPU continua independente da faixa.

Aurora Demo, Ravi Demo e Nina Demo são exemplos fictícios, sem fotografias ou identidade de alunos reais.

## O que é automático e o que exige arte

O editor aplica faixa, paleta de pele/cabelo, pequenas proporções e um pequeno emblema D no gi. Além das bases originais, o primeiro banco oferece quatro identidades adultas com rostos e silhuetas de cabelo próprias, integradas às 92 poses básicas e às 72 poses dos especiais. Veja `docs/identity-pilots/README.md`. Crianças e adolescentes ainda usam suas identidades originais. Novos formatos exigem arte e encaixes por pose. O importador legado `tools/import_identity.py` continua disponível para partes das 92 poses básicas; ele sozinho não integra essas partes aos especiais. Para conjuntos completos, use o catálogo `assets/character-identities.json` e os mapeamentos de `tools/identity_art.py`.

Uma foto não é transformada automaticamente em um lutador. O campo de referência mostra a foto somente no navegador, mediante confirmação da autorização; não envia a imagem ao servidor, ao repositório ou aos pacotes. Para menores, obtenha autorização dos responsáveis. Referências de autoria guardadas fora da página devem ficar em `private_refs/`, ignorada pelo Git, ou fora do repositório. Arte aprovada e não fotográfica pode então alimentar o pipeline de identidade.

## Arquitetura e memória

`assets/characters.json` separa identidade, corpo, faixa e aparência. `assets/character-assets.json` mantém as partes e as 92 poses autoradas de cada base. `tools/character_registry.py` valida o cadastro; `tools/compile_character.py` compõe antecipadamente rosto, cabelo, gi e pele em atlas com quadros compactados, mais faixa independente. Não contém lógica de golpes ou IA.

Perfis visuais têm chave derivada de corpo, rosto, cabelo e aparência. Nome, identificador e faixa não geram outro atlas corporal. A geometria das faixas também é compartilhada. `assets/character-visuals.json` registra os perfis; o build gera `src/character_data.lua` para Lua 5.1. Perfis antigos sem aluno são excluídos dos pacotes, embora os PNGs de autoria possam permanecer no notebook.

`src/characters.lua` escolhe e carrega apenas os recursos dos dois personagens ativos. O HTML libera os recursos desativados. O Lutro histórico mantém buffers de imagem após coleta de lixo; o cache evita recarregar a mesma imagem e recusa novas alocações que ultrapassem **80 MiB** de recursos decodificados. Se atingir esse limite após muitas trocas de aparências distintas, reinicie o cartucho. Cadastrar mais alunos que compartilham aparência não aumenta as alocações durante as partidas. Não há IA ou geração de imagem no Pi.

As 92 poses, técnicas, comandos, combos, energia, IA, física e volumes de combate existentes continuam compartilhados. A imagem varia, mas as hitboxes arcade mantêm a regra anterior; a criança continua podendo alcançar o adulto. A visualização de colisões permite conferir a diferença entre silhueta e volume virtual. A reprodução HTML mantém a meia velocidade definida anteriormente.

## Validação

`tests/character_creator.py` executa validação, limites de proporção, cadastro/edição HTTP em cópia isolada, nove personagens em três bases, duplicidade de ID, persistência e reutilização. Ele chama `tests/character_editor.cjs` para usar o editor real, criar um personagem, recarregar, selecionar P1/P2, executar contato com teclado, testar CPU e abrir o HTML offline. `tests/appearance.py` verifica recomposição, paletas e partições das poses geradas. Testes anteriores de combate, personalização e empacotamento continuam aplicáveis.

Os resultados em Windows/Chrome e a inspeção do ZIP/Lua não equivalem a execução do motor histórico Linux ou a teste físico no Raspberry Pi 3, Recalbox, GPIO e controles. Esses testes físicos continuam pendentes.
