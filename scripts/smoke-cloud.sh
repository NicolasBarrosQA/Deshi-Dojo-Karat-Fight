#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$(pwd)/.cache/cloud-tools/usr/bin:$PATH"
export SDL_AUDIODRIVER=dummy
export LIBGL_ALWAYS_SOFTWARE=1
exec xvfb-run -a python3 scripts/run.py --smoke
