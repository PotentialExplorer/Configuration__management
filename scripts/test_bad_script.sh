#!/bin/sh
# Запуск с несуществующим стартовым скриптом: ожидается ошибка.
cd "$(dirname "$0")/.." || exit 1
./run.sh --script scripts/startup/no_such_file.txt "$@"
