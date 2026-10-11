# Jogar agora no navegador

Baixe `deshi-dojo-jogar.zip`, extraia e abra `deshi-dojo-jogar.html` em um navegador de computador. O arquivo é autocontido; não exige servidor, instalação ou Internet.

Clique em **Jogar kumite** e na área do jogo. P1: setas + Z/X/A/S. P2: I/K/J/L + F/G/R/T. A tela contém as instruções e botões para diagnóstico e reinício.

Esta versão executa o mesmo `src/dojo.lua` por Fengari-web (Lua 5.3 em JavaScript), com um adaptador Canvas para as sete APIs gráficas/entrada usadas. A fonte e o cartucho TIC-80 permanecem intactos. A fonte usada é a do navegador, portanto textos e desenho podem diferir ligeiramente do TIC-80. Nenhuma compatibilidade nova com o Raspberry Pi é inferida deste adaptador.

Runtime fengari-web 0.1.4 sob MIT, baixado do npm e verificado pela integridade SHA-512 publicada no registro; origem em `runtime-provenance.json`. VM incluída integralmente no HTML. A política CSP bloqueia chamadas de rede da página.

Validação em 10/10/2026: selftest Lua/P1/P2/pontuação simultânea/troca de tela passou em Node e Chromium. Em contexto Chromium com rede offline, menu e movimentos simultâneos P1/P2 foram testados por eventos de teclado. A navegação direta ao arquivo cloud foi bloqueada pela política do ambiente; o HTML foi validado carregando seu conteúdo no navegador de teste. O aplicativo também não permite abrir URL de arquivo remoto no navegador local do usuário, por isso a entrega é um download.

Reconstrução: `python3 prototypes/tic80/browser/build_html.py`, com runtime previamente verificado em `.cache/fengari-web/`. Teste da VM: `node prototypes/tic80/browser/test_vm.cjs` (desenho isolado; não substitui o teste Chromium).
