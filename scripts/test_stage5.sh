#!/bin/sh
# Проверка команд этапа 5 на глубокой VFS; файл vfs/deep.csv
# при этом не изменяется.
cd "$(dirname "$0")/.." || exit 1
./run.sh --vfs vfs/deep.csv --script scripts/startup/stage5.txt "$@"
