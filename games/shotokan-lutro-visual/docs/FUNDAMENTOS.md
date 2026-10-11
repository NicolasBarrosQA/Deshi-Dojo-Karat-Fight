# Fundamentos e sua tradução para o jogo

Esta versão aproxima o **kihon** de um combate 2D: técnicas identificáveis, preparação, contato/desvio e retorno à guarda. São ilustrações fictícias geradas para o projeto, não captura de movimento de um praticante. A aprovação das poses pelo instrutor do dojo continua necessária, especialmente rotação, posição do punho, continuidade do braço, apoio e transferência de peso.

## Três ações, direções relativas

Frente aponta para o adversário; trás aponta para longe dele. Os comandos invertem quando os lados se invertem. Cima sozinho inicia salto; baixo sozinho usa base baixa. Com botões, as direções modificam a técnica. Direções verticais têm prioridade, exceto baixo+trás+chute, que seleciona ushiro-geri. Cima+baixo se anulam; esquerda+direita se anulam. Se as ações forem pressionadas juntas, defesa tem prioridade, depois soco, depois chute.

| Botão e direção | Técnica | Fundamento ilustrado | Linha no protótipo |
|---|---|---|---|
| Defesa + cima | Age-uke | Braço sobe diante do rosto, antebraço inclinado acima da testa e hikite da outra mão | Jōdan |
| Defesa + baixo | Gedan-barai | Preparação cruzada perto do ombro/orelha opostos, varredura para baixo e hikite | Gedan |
| Defesa + frente | Soto-uke | Preparação externa, recepção de fora para dentro, cotovelo flexionado | Chūdan |
| Defesa + trás | Uchi-uke | Preparação interna, recepção de dentro para fora, cotovelo flexionado | Chūdan |
| Defesa sem direção | Kamae | Guarda de cobertura; não equivale à execução de um uke | Chūdan |
| Soco sem direção | Gyaku-zuki | Soco com braço oposto à perna da frente, giro de quadril e hikite | Chūdan |
| Soco + frente | Oi-zuki | Avanço e soco com braço do mesmo lado da perna que termina à frente | Chūdan |
| Soco + cima | Gyaku-zuki alto | Mesma organização do soco reverso, alvo elevado | Jōdan |
| Chute sem direção | Mae-geri | Elevar joelho, estender com antepé, recolher antes de pousar | Chūdan |
| Chute + baixo | Mae-geri baixo | Câmara/extensão/recolhimento numa linha baixa | Gedan, exercício de kihon |
| Chute + frente | Mawashi-geri | Câmara lateral, giro do apoio/quadril, trajetória circular e recolhimento | Chūdan |
| Soco + trás | Kizami-zuki | Soco curto com a mão dianteira, quadril e retorno | Chūdan |
| Chute + trás | Yoko-geri kekomi | Câmara cruzada, extensão lateral conduzida pelo calcanhar/sokuto e pivô do apoio | Chūdan |
| Chute + cima | Mawashi-geri jodan | Câmara lateral, giro do quadril e extensão circular alta | Jōdan |
| Chute + baixo e trás | Ushiro-geri | Olhar por cima do ombro, virada e projeção reta do calcanhar para trás | Chūdan |
| No salto + chute | Tobi-mae-geri | Câmara e chute frontal com ambas as pernas sem apoio | Conforme altura do contato |
| No salto + frente + chute | Mawashi-geri no salto | Câmara lateral e extensão circular; perna oposta recolhida | Conforme altura do contato |
| No salto + soco | Tsuki no ar | Fundamento do soco reto aplicado ao salto; adaptação de jogo, não um novo kihon | Conforme altura do contato |

Soto/uchi seguem a convenção Shotokan descrita na tabela; outras escolas podem empregar nomes de forma diferente. Os dois protegem a linha média. O jogo não atribui arbitrariamente um ao soco e outro ao chute. O mae baixo é um exemplo de linha para estudo: um acerto abaixo da faixa **não deve ser convertido automaticamente em ponto de kumite**.

## O que a mecânica mede

A simulação avança em ticks de 60 Hz. Cada técnica tem poses, duração, preparação, janela ativa, linha e geometria próprias em `assets/techniques.json`; o build gera `src/techniques.lua` a partir desse único catálogo. Socos/chutes só geram contato quando o punho/pé se estende e a caixa pequena cruza a região correspondente do adversário. Os alcances foram ajustados aos membros nas imagens importadas. O oi também desloca o jogador durante a preparação. Aproximar demais pode fazer o pé passar além do alvo: distância importa.

Cada uke tem oito ticks de preparação. A cobertura começa no nono tick; a linha errada ou uma preparação tardia deixam o alvo aberto. Os primeiros três ticks de cobertura identificam uma recepção no tempo. Isso abre 18 ticks para iniciar um contra-ataque marcado no evento. Mantendo defesa, a posição final continua cobrindo a mesma linha, mas perde a janela inicial. Mudar direção após a técnica formar inicia outra preparação; soltar defesa inicia cinco ticks de retorno sem cobertura. Uma recepção no tempo permite soltar defesa e iniciar um soco/chute novo diretamente.

A guarda neutra tem dois ticks de preparação e cobertura média; não concede o bônus de recepção. Recepção/cobertura são aproximações de jogo, não defesas infalíveis no mundo real. Não há captura contínua de articulações nem física completa de membros. Corpos se separam; há recuperação, contato único por ataque, interrupção ao ser atingido e resolução simultânea quando ambos acertam. Segurar soco/chute não repete a técnica.

`Scene.lastContact` registra técnica, linha efetiva, distância em pixels, tick, defesa/recepção, contra-ataque, sobreposição geométrica, altura do atacante, aplicação aérea e índice da sequência. Sobreposição **não equivale a precisão técnica real**. São eventos para substituir depois a contagem de acertos por avaliação de distância, controle, tempo, zanshin e critérios do dojo. A contagem atual tem o mesmo peso para qualquer contato, sem HP/dano e sem pretensão de arbitragem oficial.

## Salto e combinações

A impulsão tem três ticks, seguida de trajetória balística discreta e pouso de cinco ticks. A altura máxima é aproximadamente 40 pixels; o salto diagonal conserva o deslocamento escolhido na partida. Não há salto duplo, invulnerabilidade no ar, cancelamento de chute estendido ou lançamento do adversário. A base baixa muda a região vulnerável e permite que um soco alto passe acima do corpo.

Cada salto permite um ataque. Socos/chutes usam poses próprias com as duas pernas sem apoio. A caixa ativa acompanha a altura do atacante; a região com maior sobreposição vertical define a linha efetiva recebida, que pode diferir da variação chudan no chão. Portanto a defesa depende do contato real no jogo, não só do nome da técnica.

As combinações são **renzoku-waza**, técnicas em sequência. Exemplos implementados: kizami → gyaku → mae; gyaku → mawashi → gyaku; mae → ushiro → gyaku. O catálogo define ligações permitidas. Nos últimos dez ticks do recolhimento, uma nova pressão pode guardar uma técnica, que começa depois da duração completa da anterior. Máximo de três; manter botão não repete e apertar antes da janela não cancela o ataque. Também é possível ligar manualmente logo após o retorno, por até 16 ticks. O contador inclui execuções que erram: não implica que todos os golpes acertaram.

A escolha dos comandos, física do salto, janelas, alcances e aplicações aéreas são convenções do jogo. Tsuki no ar não é anunciado como uma técnica básica independente. Tobi-geri pertence ao vocabulário de karatê, mas isso não torna a animação gerada uma demonstração técnica certificada. Não há arbitragem oficial implementada.

## Estudo visual

No HTML, selecione **Fundamento → Estudar técnica**, leia preparação/trajetória/recolhimento e use **Câmera lenta**, **Pausar** e **Um quadro**. É o mesmo Lua de combate executando a sequência, não um vídeo separado. O `.lutro` também mostra nome e fase da técnica durante o jogo; o painel explicativo e seletor de estudo são recursos do HTML.

São 76 poses em células de 224×144, com karateca de aproximadamente 128 pixels de altura. A extração por componente conectado recupera o pé do mawashi que cruzava a divisória da folha original, sem importá-lo na pose seguinte. Não altera a folha original. Células e atlas são verificados para não cortar membros. Fontes de arte grandes, folhas anteriores e metadados permanecem disponíveis. Espelhar um personagem ajuda o controle nos dois lados, mas não comprova biomecânica de ambos os lados ou todas as bases. O retorno do oi à guarda e transições intermediárias merecem revisão artística/técnica.

## Pesquisa consultada

Material público do **Desert Valley Shotokan**, repositório de Edwin Chandler, revisão `ea25df8a0f2af934f3663bc6446ba39529be3240`, consultado em 10/10/2026 (America/Sao_Paulo). Resumos próprios; os textos integrais não são distribuídos. URLs e hashes das páginas estão em `research-sources.json`.

- [Unit 01: bases](https://gitlab.com/edwin.chandler/desertvalleyshotokan/-/blob/ea25df8a0f2af934f3663bc6446ba39529be3240/content/resources/mcc/PED101KA/unit01.md): estabilidade, joelho dianteiro e alinhamento.
- [Unit 02: socos](https://gitlab.com/edwin.chandler/desertvalleyshotokan/-/blob/ea25df8a0f2af934f3663bc6446ba39529be3240/content/resources/mcc/PED101KA/unit02.md): organização do punho/hikite e avanço simultâneo do oi.
- [Unit 03: gedan-barai](https://gitlab.com/edwin.chandler/desertvalleyshotokan/-/blob/ea25df8a0f2af934f3663bc6446ba39529be3240/content/resources/mcc/PED101KA/unit03.md): uke como receber/desviar, três linhas, câmara oposta, varredura e quadril.
- [Unit 04: age-uke](https://gitlab.com/edwin.chandler/desertvalleyshotokan/-/blob/ea25df8a0f2af934f3663bc6446ba39529be3240/content/resources/mcc/PED101KA/unit04.md): antebraço inclinado acima da cabeça, passagem diante do rosto, outra mão recolhendo.
- [Glossário](https://gitlab.com/edwin.chandler/desertvalleyshotokan/-/blob/ea25df8a0f2af934f3663bc6446ba39529be3240/content/resources/general/glossary/_index.md) e [ensaio sobre distância e controle](https://gitlab.com/edwin.chandler/desertvalleyshotokan/-/blob/ea25df8a0f2af934f3663bc6446ba39529be3240/content/post/control-is-distance-not-speed/index.md): nomes, linhas e importância da distância.

As Units 06 e 09 consultadas contêm cabeçalhos sobre chutes e soto/uchi, mas não explicações suficientes de suas trajetórias. Os detalhes dessas técnicas no jogo são escolhas ilustrativas baseadas nos fundamentos usuais de Shotokan; não são apresentados como instruções comprovadas por essas páginas. Tentativas de consultar JKA/Wikipedia foram bloqueadas pela rede e não contam como fontes lidas. Revisão presencial do instrutor é o próximo passo para aprovar a técnica ilustrada.

Fontes comunitárias adicionais consultadas em 11/10/2026 UTC, com revisões e hashes registrados:

- [Shotokan syllabus app](https://github.com/CsabaHalmagyi/shotokan-syllabus-app/blob/d95ba1a227d17903404d9e25267cae386d78280d/app/src/main/assets/karate_syllabus.json): lista kekomi, mawashi, ushiro e sequências de técnicas. A grafia original é irregular; não é referência oficial do dojo.
- [Shotokan DB](https://github.com/muzhar01/shotokan-db/blob/a667dc928557d2d2c6732fef0ef25abbf49e6e9d/tietokanta/2_add_data_techniques_kata_kumite_syllabusinfo.sql): identifica kizami-tsuki, yoko-geri kekomi, ushiro-geri, mae/mawashi tobi-geri e combinações. O README delimita o projeto como base comunitária de conteúdo Shotokan/Seitokai.

Essas fontes sustentam o vocabulário e exemplos de encadeamento; não certificam biomecânica das imagens, tempos do jogo, graduações ou pontuação. A primeira versão das poses novas deve ser revisada com o instrutor, sobretudo pé de apoio, distinção entre yoko/ushiro e aplicações saltadas.

Para age-uke, segure defesa e depois incline para cima. Defesa também substitui a impulsão enquanto os pés ainda estão no chão; após sair do chão não há bloqueio aéreo.
