#!/bin/sh
# Запуск с VFS vfs/deep.csv и стартовым скриптом этапа 3.
cd "$(dirname "$0")/.." || exit 1
./run.sh --vfs vfs/deep.csv --script scripts/startup/stage3.txt "$@"
