#!/bin/sh
# Проверка команд этапа 4 на глубокой VFS.
cd "$(dirname "$0")/.." || exit 1
./run.sh --vfs vfs/deep.csv --script scripts/startup/stage4.txt "$@"
