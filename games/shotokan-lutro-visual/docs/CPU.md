# CPU e níveis por faixa — Lutro v05

O jogo inicia em **Contra a CPU / Fácil / faixa vermelha**. Você controla o jogador 1; não precisa de segundo teclado/controle. No browser, escolha o modo e o adversário acima da luta. Trocar a opção inicia uma partida nova. **2 jogadores** mantém os controles anteriores. **Treino livre** usa o adversário selecionado com energia/tempo ilimitados. Demonstrações suspendem a CPU; voltar à luta mantém a dificuldade escolhida. Enter/Start inicia revanche no mesmo nível.

| Nível solicitado | Perfil de jogo |
|---|---|
| Fácil · faixa vermelha | Ataques isolados, pausas maiores, menos defesas corretas e sem salto planejado |
| Médio · faixa laranja | Mais iniciativa, combinações de até duas técnicas, defesa e saltos ocasionais |
| Difícil · faixa preta | Mais pressão, combinações de até três técnicas, defesa antecipada, variação de altura e contra-ataques |

As faixas identificam os perfis no HUD, barra, indicador e menu. A arte do karateca provisório continua preservada; sua faixa desenhada não foi recolorida. Essa associação dificuldade/faixa segue a decisão do projeto, sem pretender medir a habilidade de um aluno real.

## Seleção sem mouse

No browser/viewer, **F2** abre a seleção do jogo. No cartucho, use **Select** de qualquer um dos dois ports:

1. Direcional escolhe CPU vermelha, laranja, preta ou dois jogadores.
2. Soco, chute ou Start confirma e inicia a partida.
3. Defesa ou Select fecha e retorna à partida anterior.

A luta e o relógio param enquanto o menu está aberto. Segurar direção move uma opção, sem percorrer sozinho toda a lista. A confirmação consome a pressão do botão, evitando um golpe involuntário na partida nova. Os auxiliares Start/Select continuam disponíveis nos dois ports no modo solo; direções/soco/defesa/chute do port2 não substituem a CPU. O mapeamento desses auxiliares no GPIO real ainda precisa ser identificado/testado, sem mudar a configuração do gabinete.

## Mesmas regras e golpes

`src/cpu.lua` é um controlador local: recebe observações e devolve botões. `src/main.lua` passa esses botões ao mesmo combate usado pelas pessoas. A CPU não teleporta, muda energia, aumenta dano, ignora colisões, pula recuperação nem cria técnicas. Usa somente os comandos ativos do catálogo. Assim também respeita contato único, alturas, preparação, recuperação, stun, defesa, salto e limite de sequências. O hook de pontuação técnica continua independente.

Os perfis têm atraso de observação de 22/12/6 ticks (aproximadamente 367/200/100 ms a 60 Hz), intervalos diferentes entre decisões/ataques e probabilidades de defesa/erro. As observações vêm da posição, altura, pose/fase e técnica visíveis; não dos botões, comandos guardados ou contador de stun do adversário. O estado da própria técnica é conhecido para pressionar o próximo comando no retorno permitido. Socos rápidos exigem defesa antecipada: não há bloqueio perfeito por leitura do comando humano.

A CPU usa histórico limitado a 23 observações e decisões simples, sem busca de caminhos, modelo de IA, downloads ou serviços. A pausa de impacto congela também seu raciocínio. Um gerador local determinístico usa aritmética de ponto flutuante explícita para dar o mesmo resultado em Lua 5.1 e Fengari, que tem inteiros de 32 bits. Cada round reinicia o controlador com uma semente derivada do número do round. Uma revanche repete essa semente, útil para treino/reprodução; não é aprendizado de máquina.

## O que foi comprovado

- Três partidas completas com o jogador 1 parado e nenhuma entrada do port2: CPU venceu dois rounds, resultado permaneceu e Start reiniciou. Isso verifica autonomia/rounds, não a dificuldade para uma pessoa.
- Na mesma sequência de 900 ticks do jogador 1, os perfis executaram 10/19/42 técnicas e atingiram limites de uma/duas/três técnicas ligadas. Houve defesa real no médio/difícil e bloqueio contra uma sequência física de mawashi no difícil. Os números são de uma carga sintética, não taxas de vitória humanas.
- Entradas físicas do port2 não alteraram a trajetória ou o gerador da CPU.
- Menu operado pelos dois ports: seleção, confirmação, cancelamento/pausa e restauração do segundo jogador. As cores/textos dos três perfis e quatro opções são comparados entre renderizadores.
- 1.080 ticks de replay do controlador bateram entre o núcleo histórico Lua 5.1/x86 e o browser Fengari, incluindo botões, posições/altura quantizadas a 1/16 pixel, energia, decisões e gerador.
- Browser offline com seletores reais e teclado: CPU autônoma, três níveis, comandos do jogador 1, treino, demonstração, revanche, menu e volta ao modo de dois jogadores.

Resultados: `cpu-native-results.json`, `cpu-browser-results.json`, além dos testes de combate/raster e servidor. Todos vinculam o hash do artefato exercitado. Não há promessa de balanceamento perfeito: jogar com pessoas é necessário para ajustar os níveis. Benchmarks do ambiente x86 não comprovam 60 Hz, memória/latência ou controles no Raspberry Pi 3. As pendências físicas de [COMPATIBILIDADE.md](COMPATIBILIDADE.md) continuam valendo.

Na raiz do checkout, com as ferramentas de desenvolvimento preparadas:

```bash
python3 games/shotokan-lutro-visual/tests/cpu_native.py
node games/shotokan-lutro-visual/tests/cpu_browser.cjs
```

O teste nativo chama `cpu_replay.cjs` automaticamente. Jogar pelo `scripts/play_web.py` continua requerendo somente Python standard library e um navegador.
