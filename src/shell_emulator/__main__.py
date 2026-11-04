"""Точка входа: ``python -m shell_emulator [параметры]``."""

import sys

from .config import parse_args
from .frontend import ConsoleFrontend
from .shell import Shell
from .vfs import VfsError, create_default_vfs, load_vfs


def create_frontend(config, shell):
    """Создать GUI или консольный интерфейс согласно настройкам."""
    if config.headless:
        return ConsoleFrontend(shell)
    from .gui import ShellWindow

    return ShellWindow(shell)


def load_initial_vfs(config):
    """Загрузить VFS из настроек.

    :return: кортеж ``(vfs, сообщение_об_ошибке)``. При ошибке
        загрузки используется VFS по умолчанию.
    """
    if not config.vfs_path:
        return create_default_vfs(), None
    try:
        return load_vfs(config.vfs_path, config.vfs_name), None
    except VfsError as error:
        message = f"[vfs] ошибка загрузки: {error}; используется VFS " \
            "по умолчанию"
        return create_default_vfs(), message


def start_session(config, frontend, vfs_error):
    """Показать параметры запуска и выполнить стартовый скрипт."""
    for line in config.describe():
        frontend.write(line, "info")
    if vfs_error:
        frontend.write(vfs_error, "error")
    if config.script_path:
        frontend.run_startup_script(config.script_path)


def main(argv=None):
    """Запустить эмулятор и вернуть код завершения."""
    config = parse_args(argv)
    vfs, vfs_error = load_initial_vfs(config)
    shell = Shell(vfs)
    frontend = create_frontend(config, shell)
    if config.headless:
        start_session(config, frontend, vfs_error)
    else:
        for line in config.describe():
            print(line, file=sys.stderr)
        frontend.schedule(
            lambda: start_session(config, frontend, vfs_error)
        )
    if shell.running:
        frontend.mainloop()
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())
