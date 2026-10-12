# Auditoria individual de poses

Foram inspecionados visualmente os 492 quadros lógicos: 92 poses base × três corpos, mais oito animações de nove quadros × três corpos. A revisão compara mãos, pés, cotovelos, joelhos, apoio, silhueta e continuidade com os quadros vizinhos. As folhas usam pixels reais reconstruídos dos atlases consumidos pelo jogo, sem interpolação.

Abra [o visualizador individual](pose-audit/index.html) para navegar por cada pose. [O registro JSON](pose-audit/audit.json) identifica corpo, grupo, número, observação, folha de contato e SHA-256 do PNG. O termo `reviewed` registra inspeção visual; não representa aprovação biomecânica oficial de uma técnica de karatê.

| Grupo | Problema encontrado | Correção |
|---|---|---|
| Base 51, 55 e 59, três corpos | Pé estendido com silhueta semelhante a punho; tornozelo/calcanhar pouco legíveis | Arte substituída individualmente; outras poses preservadas |
| Base 75, três corpos | Pé aéreo ambíguo; recorte e escala exigiam revisão | Substituição individual; largura do cabelo ajustada à guarda dentro de um pixel nativo |
| Ashi-barai 5–7 | Varredura com extremidades pouco legíveis | Pé, apoio e giro redesenhados; execução baixa e circular |
| Ura-mawashi 5–6 | Extremidade parecia mão | Dorsiflexão e calcanhar explícitos; quadro 6 substituído após reprovação da primeira correção |
| Ushiro 5 | Posição do pé inadequada para projeção do calcanhar | Calcanhar em linha reta e dedos para baixo; contato apenas no quadro estendido |
| Tai-sabaki 2–4 | Guarda quase estática, sem esquiva reconhecível | Pivô, giro e deslocamento curto |
| Nidan 4–6 | Duas extensões repetiam a mesma perna | Câmara intermediária e segunda extensão com perna oposta |
| Finalização 6–7 | Punho muito próximo ao tatame na continuação | Altura corrigida e pose de contato sustentada antes de recolher |
| Queda e finalização no jogo | Cabeça voltada para o atacante; soco visualmente próximo à cabeça | Queda orientada para longe do atacante e aproximação contextual antes do tsuki |

As versões anteriores das quatro poses base ficam em `assets/source/audit-corrections/before-{corpo}-{pose}.png`. As substituições ficam ao lado, com prefixo `after-`. O manifesto `assets/pose-corrections.json` impede que uma nova importação restaure automaticamente as poses reprovadas.

Arte produzida e corrigida com o modo integrado da skill imagegen. O conjunto de instruções usado pede: preservar referência de karateca e estilo; separar adulto/adolescente/criança; desenhar poses-chave da técnica; distinguir mãos de pés com tornozelo, calcanhar e dedos; manter articulações coerentes; corrigir apenas quadros reprovados; fornecer fundo transparente. Os prompts exatos e referências de cada chamada estão no histórico de ferramentas desta conversa. As fontes finais persistem em `assets/source/specials/` e `assets/source/audit-corrections/`.

O código de importação apenas recorta figuras, normaliza escala, separa tecido da faixa, espelha e empacota. Não desenha anatomia. A revisão visual é complementada por testes de espelhos, transparência binária, ancoragem no solo, escala da pose aérea e recoloração restrita à faixa. A validação no Raspberry Pi 3/Recalbox 6.1 permanece pendente, pois esse hardware e o core histórico não estão disponíveis neste ambiente Windows.
