# Fundamentos e sua tradução para o jogo

Esta versão aproxima o **kihon** de um combate 2D: técnicas identificáveis, preparação, contato/desvio e retorno à guarda. São ilustrações fictícias geradas para o projeto, não captura de movimento de um praticante. A aprovação das poses pelo instrutor do dojo continua necessária, especialmente rotação, posição do punho, continuidade do braço, apoio e transferência de peso.

## Três ações, direções relativas

Frente aponta para o adversário; trás se afasta dele. Cima sozinho salta e baixo muda a base, com ambos os pés apoiados. Direções com botão escolhem técnicas; segurar defesa antes de cima evita saltar. Esta seleção e os tempos são comandos de um jogo, não uma sequência de ensino físico.

| Comando | Técnica | Fundamento ilustrado |
|---|---|---|
| Defesa + cima | Age-uke | Antebraço inclinado acima da testa para receber/desviar a linha alta |
| Defesa + baixo | Gedan-barai | Câmara no ombro oposto e varredura para a linha baixa |
| Defesa + frente | Soto-uke | Na convenção Shotokan adotada: câmara externa e trajetória de fora para dentro |
| Defesa + trás | Uchi-uke | Câmara interna e abertura de dentro para fora |
| Primeiro soco neutro | Kizami-zuki | Mão dianteira, projeção reta e retorno |
| Segundo soco neutro, ou trás + soco | Gyaku-zuki | Braço oposto à perna dianteira; quadril, punho alinhado e hikite |
| Frente + soco | Gyaku-zuki com yori-ashi | Soco reverso coordenado com deslocamento curto da base |
| Cima + soco | Gyaku-zuki jodan | Soco reverso na linha alta |
| Baixo + soco | Gyaku-zuki em base baixa | Flexão dos joelhos, pés apoiados e soco reto |
| Chute | Mae-geri | Câmara do joelho, extensão frontal e recolhimento antes de apoiar |
| Frente + chute | Mawashi-geri | Câmara lateral, pivô do apoio/quadril e trajetória circular |
| Baixo + chute | Mae-geri gedan | Exemplo de linha baixa para estudo; não concede automaticamente ponto de kumite |
| No ar + chute | Tobi-mae-geri | Aplicação do frontal no salto, adaptada ao combate do jogo |
| No ar + soco | Tsuki no salto | Fundamento do soco reto no ar; não anunciado como novo kihon |

Soto/uchi seguem a convenção acima; nomes podem variar entre escolas. Os dois cobrem a linha média, sem atribuir arbitrariamente um ao soco e outro ao chute. A revisão do instrutor deve aprovar o movimento ilustrado antes de usá-lo como demonstração didática.

## Representação selecionada

O repertório ativo tem oito ataques no chão, dois no salto e quatro uke, além da guarda neutra. Oi, yoko, ushiro e mawashi alto/aéreo permanecem em `assets/techniques.json`, com `playable=false`, e suas folhas/poses estão preservadas. Os giros não deixam a trajetória e o apoio claros o bastante. A antiga pose de oi usa braço reverso e avanço curto; o comando ativo foi renomeado gyaku com yori-ashi. Não se deve ensinar um fundamento apenas porque o catálogo atribui um nome à imagem.

Foram importadas 92 poses em células 224×144: novas reações de tronco/cabeça e uma base baixa com pés apoiados são usadas no combate. As tentativas de giro novas também ficam guardadas, sem entrar na luta. O karateca fictício tem cerca de 128 pixels de altura. O importador extrai cada silhueta conectada na folha inteira; mantém o pé do mawashi em sua pose mesmo quando ele cruza a grade e impede fragmentos na seguinte. Os originais não são alterados. Os membros ainda precisam de revisão de alinhamento, continuidade entre quadros, apoio, quadril e hikite. Não há captura contínua de articulações.

## Ritmo e contato

A simulação usa ticks de 60 Hz. O catálogo define poses, tempos, preparação, janela ativa, alcance e altura. Kizami prepara por três ticks, gyaku por quatro e mae por cinco; o contato é permitido na extensão. Depois de acertar, há três ticks de pausa visual e recolhimento, em vez de manter o punho/pé dentro do oponente. A reação aparece imediatamente; o defensor recua e se recompõe. Esses tempos, energia, reação e recuo são convenções de arcade.

A barreira de 88 pixels entre centros preserva a ordem anterior aos movimentos e resolve penetração por quem avançou, inclusive em paredes e saltos. Ela separa corpos; a extensão de um braço/perna pode sobrepor o alvo para representar o acerto. As três regiões vulneráveis seguem a altura da pose real; uma base mais baixa muda a linha efetivamente atingida. Um mawashi nominalmente chudan pode chegar à cabeça de um alvo mais baixo. A linha recebida vem da maior interseção vertical, em vez de ser imposta pelo nome.

Os uke preparam por três ticks e cobrem a partir do quarto; os primeiros três ticks de cobertura identificam recepção no tempo. Uma recepção abre 16 ticks de contra-ataque marcado. Guarda neutra prepara por dois e cobre a linha média sem bônus de recepção. Mudar direção prepara outra defesa; soltar libera. Defesa errada/tardia não protege. Há um contato por ataque, interrupção ao receber golpe e resolução simultânea quando ambos acertam. Não há dano ao bloquear.

Pressões novas ficam guardadas por até 24 ticks, inclusive durante pausa de impacto, stun, defesa e recolhimento. Só começam quando o estado permite; o comando não cancela a extensão. Nos encadeamentos, `link_at` exige retorno antes da técnica seguinte. Até três técnicas podem ser ligadas; depois há oito ticks de recomposição. Botão mantido não repete. A sequência inicial é **kizami → gyaku → mae**, com soco, soco, chute. O contador COMBO só aumenta se o contato seguinte ocorrer enquanto o defensor ainda se recompõe. Sequência executada e acertos consecutivos são métricas diferentes.

O salto tem dois ticks de impulsão no chão, lançamento no terceiro, altura máxima próxima de 44 pixels e dois ticks de pouso. Um ataque por salto, sem defesa aérea, salto duplo ou lançamento do oponente. Segurar cima não inicia outro salto depois do pouso. A caixa do ataque acompanha a altura real e a defesa depende da linha recebida.

## Regras de arcade e futura pontuação

**Lutar** usa energia, 60 segundos e dois rounds vencidos. O tempo da simulação para durante a pausa de impacto. **Treino livre** e demonstração mantêm energia/tempo. As regras de partida são separadas dos eventos de técnica: energia não é a única informação da arquitetura.

`Scene.lastContact` e o observador opcional `Scene.onContact(event)` recebem técnica, linha efetiva, distância em pixels, tick, defesa/recepção, contra-ataque, sobreposição, coordenadas do contato, altura/aplicação aérea, índice da sequência e número de acertos consecutivos. O teste verifica esses eventos tanto no treino quanto na luta. Sobreposição geométrica **não certifica precisão técnica**. Uma camada futura pode avaliar distância, controle, tempo, zanshin e critérios do dojo sem mudar a simulação ou os comandos. Não há arbitragem oficial.

## Estudo visual

Abra **Aprender os golpes e ver todos os comandos** no HTML. O nome em português e a fase aparecem durante a luta; indicadores acendem ao pressionar. No painel opcional, **Ver movimento**, câmera lenta, pausa e quadro único permitem observar a mesma técnica executada pelo Lua. Volte com **Lutar**. O cartucho mostra nome/fase; o painel textual é do browser. A arte gerada continua ilustrativa e não é instrução física certificada.

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
