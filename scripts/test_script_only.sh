#!/bin/sh
# Запуск только со стартовым скриптом.
cd "$(dirname "$0")/.." || exit 1
./run.sh --script scripts/startup/stage2.txt "$@"
