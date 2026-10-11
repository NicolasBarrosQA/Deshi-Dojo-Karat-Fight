# Deshi Dojo — Karat Fight

Base para um jogo de luta 2D com alunos do dojo e golpes de karate Shotokan.
O protótipo atual usa **Lutro**, com dois jogadores e fundamentos Shotokan. A base **IKEMEN GO 1.0.0** e os protótipos TIC-80 continuam preservados.

## Jogar pelo clone, em localhost

Requer somente Python 3.11+ e um navegador atual. Na primeira vez:

```sh
git clone https://github.com/NicolasBarrosQA/Deshi-Dojo-Karat-Fight.git
cd Deshi-Dojo-Karat-Fight
python scripts/play_web.py
```

No Linux/macOS, use `python3`; no Windows, `py -3` também funciona. O comando abre o navegador em `http://localhost:8000` e mantém o servidor no terminal. Não precisa de ZIP, npm, instalação do motor ou Internet para jogar.

Para receber novas versões, execute `git pull` nessa mesma pasta e atualize a página com F5. O servidor reconstrói o HTML quando a fonte muda, sem empacotar ZIPs. Ctrl+C encerra. Se a porta estiver ocupada, execute `python scripts/play_web.py --port 8001`; `--no-open` evita abrir o navegador automaticamente.

Controles: P1 setas, Z soco, X defesa, A chute; P2 I/K/J/L direções, F soco, G defesa, H chute. Cima sozinho salta; baixo sozinho usa base baixa. Há ataques aéreos e sequências de até três técnicas, mantendo três botões por jogador. Veja [os comandos e fundamentos do protótipo](games/shotokan-lutro-visual/README.md). O Raspberry Pi/GPIO e as poses ainda precisam dos testes físicos e da revisão do instrutor.

## Base IKEMEN preservada

O primeiro protótipo IKEMEN executa Kung Fu Man versus Kung Fu Man; os alunos e os golpes originais nessa base ainda serão criados. As instruções abaixo se referem a esse motor.

## Instalar e jogar

Requer Python **3.11+**, Internet na primeira instalação e PC x86-64.
No Linux: glibc 2.35+, ambiente gráfico e GPU com OpenGL 3.3 (ou renderização Mesa equivalente), além das bibliotecas de sistema GL/X11/GTK3.
No Windows: Windows 10+ 64 bits e driver gráfico compatível. Windows está previsto no instalador, mas ainda não foi validado neste ambiente Linux.

Na raiz do repositório:

```sh
python scripts/install.py
python scripts/run.py
```

No Windows, também é possível usar `py -3` no lugar de `python`.
O menu oficial permite configurar controles e iniciar partidas locais.
Para assistir a uma luta automática entre os exemplos:

```sh
python scripts/run.py --demo
```

Para um teste curto que só passa quando o motor registra o resultado da luta:

```sh
python scripts/run.py --smoke
```

No ambiente de nuvem Debian 13, preparar e testar sem monitor:

```sh
bash scripts/setup-cloud.sh
bash scripts/smoke-cloud.sh
```

Em outros ambientes Linux sem monitor, com Xvfb instalado:

```sh
SDL_AUDIODRIVER=dummy LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python scripts/run.py --smoke
```

## Organização

- `engine/`: versão, URLs e checksums oficiais fixos.
- `game/chars/`: personagens originais dos alunos.
- `game/stages/`: cenário do dojo.
- `game/data/`: menus, seleção e barras de vida.
- `game/sound/`: músicas e efeitos.
- `scripts/`: instalação e execução.
- `licenses/` e `docs/ASSETS.md`: avisos e origem dos recursos.
- `.runtime/`: pacote completo extraído, ignorado pelo Git.
- `.cache/`: downloads e resultados de testes, ignorados pelo Git.

O instalador verifica SHA-256 antes de extrair e preserva instalações existentes.
A execução copia os arquivos de `game/` para o runtime; edite os originais em `game/`, pois a cópia de execução é substituída no próximo início.
A remoção de um arquivo de `game/` não remove automaticamente sua cópia do runtime. Para retornar ao pacote limpo, preserve configurações locais e remova `.runtime/` antes de reinstalar.
Não guardar alterações criativas apenas em `.runtime/`, pois ela não é versionada.

## Próximo marco

Criar dois alunos, um cenário do dojo e quatro golpes por aluno: oi-zuki, gyaku-zuki, mae-geri e mawashi-geri.

Os exemplos contêm recursos **não comerciais**. Consulte [os créditos e as licenças](docs/ASSETS.md) antes de distribuir o jogo.
