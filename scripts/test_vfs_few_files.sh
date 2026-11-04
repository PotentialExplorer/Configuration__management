#!/bin/sh
# Запуск с VFS vfs/few_files.csv и стартовым скриптом этапа 3.
cd "$(dirname "$0")/.." || exit 1
./run.sh --vfs vfs/few_files.csv --script scripts/startup/stage3.txt "$@"
