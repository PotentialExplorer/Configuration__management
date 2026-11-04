#!/bin/sh
# Запуск со всеми параметрами; скрипт завершается командой exit.
cd "$(dirname "$0")/.." || exit 1
./run.sh --vfs vfs/minimal.csv --script scripts/startup/with_exit.txt "$@"
