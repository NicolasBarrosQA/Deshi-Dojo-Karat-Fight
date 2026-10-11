# Pressão e defesa — Lutro v06

O relato de ganhar só apertando soco revelou uma falha reproduzível. Na v05, a primeira sequência deixava uma abertura muito curta, a CPU abandonava os comandos durante o impacto e ficava sem guarda durante a própria recuperação. Um ataque já no buffer também podia tomar prioridade sobre uma nova pressão de defesa. Contar somente técnicas ligadas não tratava a repetição da mesma técnica.

## Correção nas regras comuns

- **Combo preservado:** soco → soco → chute ainda produz três contatos consecutivos nas duas portas e orientações, com buffer antecipado.
- **Abertura real:** somente uma ligação prevista no catálogo pode pular o término de um ataque. Ao finalizar sem ligação, são 16 ticks (aproximadamente 267 ms a 60 Hz) antes de iniciar outro ataque no chão. Inclui o terceiro golpe e a repetição da mesma técnica. Durante a abertura, é possível mover, defender e saltar. Esses tempos são regras de arcade.
- **Defesa tem prioridade:** uma nova pressão de defesa remove o ataque anterior do buffer, inclusive durante impacto/recolhimento. Não interrompe a extensão do golpe em curso. Uma pressão posterior de soco enquanto a defesa está mantida continua permitindo contra-atacar.
- **Cobertura clara:** segure X/G. Guarda neutra, soto-uke e uchi-uke cobrem a linha média; age-uke a alta; gedan-barai a baixa. O indicador GUARDA/RECEBE mostra a altura protegida. PREPARA e IMPACTO ainda não protegem. Mudar a defesa reinicia a preparação. Um combo verdadeiro não pode ser defendido no meio; a guarda entra na abertura seguinte.

Dano, energia, stun, recuo e sprites não foram alterados. A preparação continua sendo dois ticks para guarda neutra e três para uke; bloqueios não tiram energia. CPU e pessoas passam pela mesma máquina de combate. Não foi acrescentada invulnerabilidade ou bônus à CPU.

## Controlador local

A CPU pode segurar a defesa durante impacto, mantendo seu atraso de observação. Reconhece repetição pela linha/técnica/fase visíveis, tenta contra-atacar a abertura e protege a própria recuperação. As probabilidades e erros diferem por faixa. Só pede continuação depois de contato confirmado e escolhe avanço/alcance para evitar oferecer um chute lento após um soco que errou. Não lê teclas/buffer/stun do adversário, não altera jogadores e não usa rede.

## Evidência e limites

`tests/pressure.py` executou 48 partidas no core histórico Lua 5.1/x86: três níveis, ciclos de pressão/soltura de 2/4/6/10 ticks, centro e canto, duas orientações. Só usa o botão de soco; posições iniciais dão iniciativa à primeira sequência humana. Sem injetar contatos ou mudar energia. Usa a semente normal do primeiro round, 1080.

| Perfil | Resultado desse cenário fixo |
|---|---|
| Vermelha/fácil | Perdeu as 16 partidas; ainda admite perfect em alguns cenários |
| Laranja/médio | Perdeu as 16, mas respondeu com golpes em todas |
| Preta/difícil | Venceu 14/16; perdeu na cadência de 10 ticks no centro, nas duas orientações |

Antes, na mesma reprodução de 24 casos em uma orientação, a humana venceu todos; fácil/médio não acertaram nenhum golpe. Depois, a vitória por spam deixou de ser automática no difícil. Essas amostras verificam a regressão, não medem dificuldade contra pessoas ou garantem que todo perfect seja impossível.

Os testes nativos também verificam que segurar guarda após os três primeiros socos bloqueia o seguinte nos dois cantos, e que a defesa substitui um soco guardado durante preparação ou stun, nas duas portas/orientações. Os 40 pares ataque/defesa no chão e dez no ar continuam cobrindo alturas corretas/incorretas e perda de energia. Teclado real no Chromium reproduz esses casos e partidas completas de soco repetido nos três níveis, sem HTTP externo. `pressure-results.json`, `native-results.json`, `browser-results.json` e os relatórios da CPU vinculam o artefato testado.

Para repetir na raiz do checkout preparado:

```bash
python3 games/shotokan-lutro-visual/tests/pressure.py
python3 games/shotokan-lutro-visual/tests/native.py
node games/shotokan-lutro-visual/tests/browser.cjs
node games/shotokan-lutro-visual/tests/cpu_browser.cjs
```

Ainda precisamos de partidas humanas para ajustar sensação de recuperação, alturas e diferenças entre faixas. Raspberry Pi, GPIO, teclado Windows real e revisão das técnicas pelo instrutor permanecem pendentes. Nenhum arquivo do gabinete foi acessado.
