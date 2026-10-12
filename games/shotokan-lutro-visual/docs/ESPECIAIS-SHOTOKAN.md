# Especiais e auditoria de assets

Implementação na branch `codex/shotokan-specials`, preservando o trabalho de personalização presente na árvore de trabalho. Catálogo normal, seleção, treino, energia, rounds e cobertura anterior das defesas continuam integrados.

## Comandos

Frente/trás dependem da orientação do lutador. O parser usa janela de 22 ticks, intervalo máximo de 10 ticks e quatro ticks para associar o botão à direção final. Requer transições direcionais completas; caminhada ou guarda isoladas não completam um comando. A tolerância opcional para joystick de quatro direções fica desativada por padrão.

| Técnica | Comando | Dano Arcade inicial |
|---|---|---|
| De-ashi-barai | ↓ ↘ → + chute | 4 |
| Finalização da própria rasteira | Novo ↓ + defesa, perto do adversário caído | 12 adicionais |
| Ura-mawashi-geri | ← ↙ ↓ ↘ → + chute | 18 |
| Ushiro-geri | → ↘ ↓ ↙ ← + chute | 20 |
| Tai-sabaki | ↓ ↙ ← + defesa; novo soco na janela de resposta | 10 no contra-ataque |
| Renzoku-zuki | → ↓ ↘ + soco | 6 + 9 |
| Nidan-geri | → ↓ ↘ + chute | 7 + 10 |

São valores de combate Arcade, sem equivalência com pontuação oficial de kumite. Preparação, contatos, dano, recuperação, janela de finalização e distâncias ficam em `assets/specials.json`.

## Queda e finalização

A rasteira interrompe o alvo, aplica desequilíbrio e queda desenhada quadro a quadro. A janela de 38 ticks começa após a queda de 36 ticks. O atacante precisa recuperar sua ação e enviar um segundo comando fresco; segurar defesa previamente não dispara o tsuki. A permissão pertence ao atacante da derrubada, é consumida uma única vez e exige alcance válido. Sem permissão, fora do alcance ou após a janela, baixo + defesa continua gedan-barai.

O alvo permanece no chão durante a finalização, não ataca e só inicia a levantada quando a ação termina. Ataques normais não causam dano repetido ao caído. A separação entre centros permite aproximação contextual durante a queda e retorna gradualmente aos 88 pixels normais na levantada. Não há troca artificial de lados. A queda orienta a cabeça para longe do atacante; a aproximação permite alcançar o tronco. O efeito discreto de contato segue a posição visual do punho.

A CPU usa sequências de direções e botões normais, com observação atrasada do oponente, chance de execução por dificuldade e recuperação comum. Os especiais foram limitados sob pressão para preservar a resposta contra socos repetidos.

## Entregáveis

- `src/motion.lua`, `src/specials.lua` e integração no motor, CPU, renderer e áudio.
- `dist/deshi-dojo-visual.html`: página única offline, incluindo imagens e sons.
- `dist/deshi-dojo-visual.lutro`: cartucho ZIP histórico com caminhos portáveis.
- `assets/source/specials/`: oito folhas de arte fonte, três corpos × nove quadros.
- `src/assets/special-*.png`: atlases compactos de corpo/faixa, ambos os lados e perfis personalizados.
- `docs/pose-audit/index.html` e `audit.json`: revisão individual das 492 poses.
- `docs/special-captures/*.gif`: seis capturas reais do HTML/Lua, dirigidas por teclas DOM, sem injeção de ações prontas.
- `docs/special-captures/capture-results.json` e `*/trace.json`: hash do HTML, entradas, estados, quadros e contatos observados.

Os GIFs usam quadros reais do canvas a cada dois ticks de simulação a 60 Hz e reprodução de estudo em aproximadamente 0,5×. A captura da sequência principal registra contatos distintos de 4 e 12 pontos e recuperação dos dois personagens. Os demais GIFs mostram os contatos individuais dos especiais implementados.

Capturas: [rasteira e finalização completas](special-captures/ashi-sequence.gif), [Ura-mawashi](special-captures/ura_mawashi.gif), [Ushiro](special-captures/ushiro.gif), [Tai-sabaki e contra-ataque](special-captures/tai_sabaki.gif), [Renzoku](special-captures/renzoku.gif) e [Nidan](special-captures/nidan.gif).

Assets: [auditoria individual](pose-audit/index.html), [comparação antes/depois](pose-audit/corrections-before-after.png) e [fonte da rasteira](../assets/source/specials/ashi_barai.png). Execução: [HTML offline](../dist/deshi-dojo-visual.html) e [cartucho Lutro](../dist/deshi-dojo-visual.lutro).

## Validação e limites

Risco de regressão: alto, por integrar novos estados no combate e na geração de assets. A estratégia combina parser puro, integração por teclado real no navegador offline, reconstrução dos sprites e validação do cartucho.

Resultados detalhados ficam em `docs/specials-results.json`, `special-assets-results.json`, `personalization-results.json`, `appearance-results.json`, `browser-results.json`, `cpu-browser-results.json` e `special-captures/capture-results.json`. Cada resultado que possui `artifact_sha256` identifica exatamente o HTML testado; hashes anteriores correspondem a verificações feitas antes dos últimos ajustes específicos da finalização.

Foram verificados comandos nos dois lados, P1/P2, prioridade contextual, bloqueio baixo, erro, expiração, alcance, bordas, recuperação, um golpe por queda, fim de round, energia em treino e especiais da CPU por entradas normais. Os testes gráficos verificam as 276 poses base/2.208 variantes de faixa e 216 poses especiais/1.728 variantes de faixa. Testes automáticos não avaliam anatomia: a inspeção visual separada e suas correções estão em [AUDITORIA-DE-POSES.md](AUDITORIA-DE-POSES.md).

O core histórico e o Raspberry Pi 3/Recalbox 6.1 físico não foram executados neste Windows. A sintaxe usa Lua 5.1, os módulos compartilham o mesmo código entre cartucho e HTML, os sons usam WAV PCM mono de 44,1 kHz, e os especiais são carregados sob demanda no renderer nativo. O teto de retenção é 128 MiB; desempenho, controles físicos, consumo real de memória e áudio no hardware permanecem pendentes.
