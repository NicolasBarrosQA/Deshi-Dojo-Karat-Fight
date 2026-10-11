#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/install.py
if command -v Xvfb >/dev/null; then exit 0; fi
TOOLS="$(pwd)/.cache/cloud-tools"
if [[ -x "$TOOLS/usr/bin/Xvfb" ]]; then exit 0; fi
# Instalação local de Xvfb, sem escrever nos diretórios de sistema.
# Este caminho foi validado em Debian 13 (trixie).
if ! command -v xauth >/dev/null; then
  echo 'Instale xauth pelo gerenciador de pacotes para executar xvfb-run.' >&2
  exit 1
fi
. /etc/os-release
if [[ "$ID" != debian || "$VERSION_CODENAME" != trixie ]]; then
  echo 'Instale Xvfb pelo gerenciador da sua distribuição.' >&2
  exit 1
fi
APT_DIR="$(pwd)/.cache/cloud-apt"
mkdir -p "$APT_DIR/lists/partial" "$APT_DIR/cache/archives/partial" "$TOOLS"
printf '%s\n' 'deb https://deb.debian.org/debian trixie main' > "$APT_DIR/sources.list"
OPTIONS=(-o "Dir::Etc::sourcelist=$APT_DIR/sources.list" -o Dir::Etc::sourceparts=- -o "Dir::State::lists=$APT_DIR/lists" -o "Dir::Cache=$APT_DIR/cache")
apt-get "${OPTIONS[@]}" update
(cd "$APT_DIR" && apt-get "${OPTIONS[@]}" download xvfb)
for package in "$APT_DIR"/xvfb_*.deb; do dpkg-deb -x "$package" "$TOOLS"; done
