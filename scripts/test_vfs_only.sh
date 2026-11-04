#!/bin/sh
# Запуск только с путём к VFS.
cd "$(dirname "$0")/.." || exit 1
./run.sh --vfs vfs/minimal.csv "$@"
