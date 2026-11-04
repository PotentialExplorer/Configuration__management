#!/bin/sh
# Ошибки загрузки VFS: файл не найден и неверный формат.
# По умолчанию запускается в консольном режиме, чтобы показать
# все случаи подряд.
cd "$(dirname "$0")/.." || exit 1
for vfs in vfs/no_such.csv vfs/broken_header.csv \
    vfs/broken_base64.csv vfs/broken_tree.csv; do
    echo "=== $vfs"
    ./run.sh --headless --vfs "$vfs" "$@" < /dev/null
    echo
done
