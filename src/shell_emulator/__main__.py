"""Точка входа: ``python -m shell_emulator``."""

import sys

from .shell import Shell


def main():
    """Запустить эмулятор в графическом режиме."""
    from .gui import ShellWindow

    shell = Shell()
    window = ShellWindow(shell)
    window.mainloop()
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())
