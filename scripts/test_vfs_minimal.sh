#!/bin/sh
# Запуск с VFS vfs/minimal.csv и стартовым скриптом этапа 3.
cd "$(dirname "$0")/.." || exit 1
./run.sh --vfs vfs/minimal.csv --script scripts/startup/stage3.txt "$@"
