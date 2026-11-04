"""Точка входа: ``python -m shell_emulator [параметры]``."""

import sys

from .config import parse_args
from .frontend import ConsoleFrontend
from .shell import Shell


def create_frontend(config, shell):
    """Создать GUI или консольный интерфейс согласно настройкам."""
    if config.headless:
        return ConsoleFrontend(shell)
    from .gui import ShellWindow

    return ShellWindow(shell)


def start_session(config, frontend):
    """Показать параметры запуска и выполнить стартовый скрипт."""
    for line in config.describe():
        frontend.write(line, "info")
    if config.script_path:
        frontend.run_startup_script(config.script_path)


def main(argv=None):
    """Запустить эмулятор и вернуть код завершения."""
    config = parse_args(argv)
    shell = Shell(config.vfs_name)
    frontend = create_frontend(config, shell)
    if config.headless:
        start_session(config, frontend)
    else:
        for line in config.describe():
            print(line, file=sys.stderr)
        frontend.schedule(lambda: start_session(config, frontend))
    if shell.running:
        frontend.mainloop()
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())
