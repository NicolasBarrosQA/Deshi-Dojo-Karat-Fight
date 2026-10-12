# Correção do encaixe e das sobreposições

A primeira entrega passou nos testes de dimensões e exportação, mas esses testes não garantiam o encaixe anatômico. O relato mostrou isso na pose 15 do adulto. A marcação anterior usava uma região de pele conectada: quando a mão tocava a cabeça, braço e crânio eram medidos juntos. A largura e o centro do cabelo ficavam errados.

Outra falha era inferir roupa branca pelas cores do personagem já recolorido. Partes claras da pele podiam ser tratadas como roupa e reaparecer por cima do cabelo. A máscara não pode depender do tom de pele escolhido.

O novo registro identifica o interior craniano, mede seu centro e usa largura/altura independentes para encaixar a vista de cabelo. As 1.092 marcações foram reconstruídas. As máscaras de sobreposição vêm da arte neutra original, antes da recoloração. O antebraço levantado mantém sua posição à frente; os pixels do couro cabeludo deixam de atravessar o cabelo. O ponto de contato inferior do punho na pose enviada tem uma exceção explícita revisada na fonte original, em `hair-binding-overrides.json`.

O editor agora usa uma revisão das fontes nas URLs dos atlases. Assim, um novo desenho compilado não reutiliza a imagem antiga em cache. IDs, nomes, proporções, corpo, faixa e cores continuam preservados. As três artes aprovadas não foram substituídas.

Validação que complementa os testes anteriores:

- Seis referências de guarda verificadas independentemente do algoritmo de encaixe.
- 216 verificações de cobertura do topo da cabeça: seis corpos × três cortes × 12 tons de pele.
- Nove verificações da pose do relato: três cortes × pele original, clara e retinta; pixels do antebraço preservados.
- Captura da mesma pose no editor real, com adulto, pele clara, cabelo grisalho e faixa preta: `reported-pose-corrected.png`.
- Exportação isolada dos seis corpos e execução dos 90 quadros especiais em P1/P2; CPU/cadastros originais preservados.
- Novos GIFs reais com defesa alta nos dois ports, salto, nidan e ushiro. Estes substituem a demonstração anterior para avaliar as sobreposições durante o combate.
- Verificações de dimensões, proporções, materiais, integridade dos pacotes e cache do editor.

Os GIFs vêm de um HTML exportado na fixture de teste; seu elenco de demonstração não altera o cadastro do desenvolvedor. Cada quadro decodificado é comparado com a captura do jogo. O Raspberry Pi físico não foi executado.
