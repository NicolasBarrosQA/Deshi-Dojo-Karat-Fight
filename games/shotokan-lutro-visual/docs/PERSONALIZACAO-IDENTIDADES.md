# Personalização por identidade — proposta de evolução

Atualização: foram implementadas bases corporais femininas próprias para criança, adolescente e adulta, com 492 poses e seleção no criador e no jogo. Consulte [a entrega das bases femininas](female-bodies/README.md). O banco de quatro identidades adultas permanece na base anterior; combinar essas cabeças com as novas bases é uma integração artística separada.

## Diagnóstico do código atual

O criador dispõe de um rosto e um cabelo originais por corpo (criança,
adolescente e adulto). Paletas, largura e altura não oferecem diversidade
anatômica real. Os campos de rosto/cabelo aceitam recursos importados, mas
o banco artístico ainda não oferece essa variedade.

`tools/import_identity.py` encaixa vistas em 92 poses básicas. Isso não
garante que uma peça cubra corretamente a cabeça anterior: um cabelo menor,
por exemplo, exige remover a silhueta antiga e reconstruir o couro cabeludo.

`tools/compile_special_profiles.py` aplica aparência à base dos especiais,
mas não compõe os recursos de rosto e cabelo escolhidos. Uma identidade nova
precisa ser integrada a esse caminho antes de ser considerada funcional.

## Resultado pretendido

Cada aluno deve ser reconhecível pela forma do rosto, cabelo e silhueta,
mesmo com a mesma faixa e as mesmas cores de outro aluno. A identidade deve
permanecer durante guarda, golpes, saltos, giros, queda e levantamento.

O editor deve mostrar escolhas ilustradas e nomes claros. Primeiro oferece
personagens completos; depois permite combinar peças compatíveis. Cor passa
a ser um ajuste da identidade, não seu principal recurso.

## Banco artístico inicial proposto

Começar com quatro identidades piloto numa mesma faixa etária permite
comparar diferenças reais sem confundi-las com tamanho do corpo:

- Rosto arredondado, cabelo curto e cacheado.
- Rosto alongado, cabelo liso curto com franja.
- Rosto com mandíbula mais marcada, cabelo raspado.
- Rosto oval, cabelo comprido preso, com volume e contorno próprios.

Essas são propostas de variedade, não assets já disponíveis. Formatos de
olhos, sobrancelhas, nariz, boca, mandíbula e orelhas precisam ser desenhados
como conjuntos coerentes e legíveis na resolução nativa. Evitar dezenas de
controles de detalhes que desaparecem durante a luta.

Após validar o piloto, ampliar para crianças, adolescentes e adultos com
arte adequada às proporções de cada grupo. Novos portes corporais devem ter
silhuetas desenhadas; esticar o mesmo desenho não substitui essa autoria.

## Composição de todas as animações

1. Preparar bases sem a identidade antiga, com pescoço e couro cabeludo
   completos. Remover cabeça/cabelo antigos apenas por máscaras autoradas,
   sem apagar mãos ou pés de cores semelhantes.
2. Desenhar vistas necessárias de cada cabeça: frontal, três quartos,
   perfil e posterior, mais inclinações exigidas pelas poses.
3. Mapear encaixe, orientação e sobreposição por pose. Cabelo atrás do corpo
   e cabelo à frente precisam de camadas distintas quando a pose exigir.
4. Usar a mesma identidade nas 92 poses básicas e nas 72 poses dos oito
   grupos especiais de cada corpo. Não colar uma cabeça frontal em giros ou
   quedas; nesses casos escolher ou desenhar a vista correta.
5. Compilar atlas antecipadamente para HTML e Lutro. O jogo continua offline
   e não precisa gerar imagens durante a luta.
6. Incluir identidade e conteúdo dos recursos nas assinaturas do cache dos
   dois compiladores. Uma edição artística deve invalidar ambos.

## Ordem de entrega

Primeiro produzir e revisar os quatro pilotos em guarda, perfil, golpe com
rotação e posição no chão. Essa amostra resolve estilo e encaixe antes de
espalhar defeitos por centenas de quadros. Depois integrar uma identidade
completa em todas as poses, validar no jogo e expandir o banco e o editor.

## Critérios de aceitação

- Quatro identidades reconhecíveis sem depender das cores.
- Nenhuma sobra do cabelo ou rosto anterior, inclusive com cabelo raspado.
- Cabeça com tamanho consistente entre poses, sem deformar mãos ou pés.
- Mesma identidade em ataques básicos e especiais, em P1 e P2.
- Faixa recolorida apenas na sua camada, inclusive nas pontas.
- Retratos e prévias incluem o cabelo completo; não usam um recorte fixo
  que corte estilos maiores.
- Revisão visual pose por pose; testes de máscaras e encaixes complementam
  essa revisão, sem alegar que verificam anatomia.
- Comparação de memória e tamanho dos pacotes com a entrega atual; ensaio
  físico no Raspberry Pi/Recalbox permanece necessário para confirmar o
  orçamento real do hardware.

## Estado desta etapa

Primeiro banco implementado: quatro identidades adultas, oito vistas de
cada cabeça e integração das 164 poses básicas/especiais por identidade.
O editor oferece miniaturas e os quatro pilotos estão cadastrados no jogo.
Relatório e evidências: `identity-pilots/README.md`.

As identidades de criança/adolescente, portes autorados e combinações
independentes de rosto/cabelo continuam como próximas etapas. Neste piloto,
as identidades usam conjuntos completos para preservar a coerência artística.
