# Validação da base

Validado em 10/10/2026, Linux x86-64 / Debian 13:

- Download oficial IKEMEN GO 1.0.0 verificado por SHA-256.
- Instalação e repetição da instalação concluídas, preservando o runtime.
- Inicialização gráfica com Xvfb e Mesa llvmpipe (OpenGL 4.5).
- Tela inicial e menu oficial inspecionados; Enter avança o aviso inicial.
- Luta automática KFM versus KFM concluída com resultado registrado, dano e vencedor.
- `bash scripts/setup-cloud.sh` repetido e `bash scripts/smoke-cloud.sh` concluído com código 0.

Limitações do pacote oficial: avisos de parâmetros `x, y` no estado 1027 de KFM e referência a `sound/Title.mp3` ausente. Não impediram menu nem combate; a música de título não foi validada. Nenhum recurso de terceiros foi baixado para substituir esse áudio.

Windows: instalador configurado com o checksum oficial, execução ainda não testada.
Personagens do dojo, golpes Shotokan e cenário original: ainda não implementados.
