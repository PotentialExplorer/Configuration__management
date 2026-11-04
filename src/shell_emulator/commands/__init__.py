"""Встроенные команды эмулятора.

Каждая команда — функция вида ``command(shell, args) -> str``.
Она возвращает текст для вывода или возбуждает :class:`CommandError`.
"""

from .base import CommandError
from .info import cmd_cal, cmd_date
from .navigation import cmd_cd, cmd_ls, cmd_tree
from .session import cmd_exit, cmd_vfs_info

COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "tree": cmd_tree,
    "date": cmd_date,
    "cal": cmd_cal,
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
}

__all__ = ["COMMANDS", "CommandError"]
