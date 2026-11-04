"""Параметры запуска эмулятора."""

import argparse
import os
from dataclasses import dataclass

from .vfs import DEFAULT_NAME as DEFAULT_VFS_NAME


@dataclass
class Config:
    """Настройки, заданные пользователем при запуске.

    :ivar vfs_path: путь к физическому расположению VFS или ``None``.
    :ivar script_path: путь к стартовому скрипту или ``None``.
    :ivar headless: запуск без GUI (вывод в консоль).
    """

    vfs_path: str | None = None
    script_path: str | None = None
    headless: bool = False

    @property
    def vfs_name(self):
        """Имя VFS: имя файла без расширения или имя по умолчанию."""
        if not self.vfs_path:
            return DEFAULT_VFS_NAME
        base = os.path.basename(os.path.normpath(self.vfs_path))
        return os.path.splitext(base)[0] or DEFAULT_VFS_NAME

    def describe(self):
        """Вернуть строки отладочного вывода всех параметров."""
        missing = "<не задан>"
        return [
            f"[config] vfs      = {self.vfs_path or missing}",
            f"[config] vfs name = {self.vfs_name}",
            f"[config] script   = {self.script_path or missing}",
            f"[config] headless = {self.headless}",
        ]


def build_parser():
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="shell_emulator",
        description="Эмулятор командной оболочки UNIX с GUI.",
    )
    parser.add_argument(
        "--vfs", dest="vfs_path", metavar="PATH",
        help="путь к физическому расположению VFS (CSV-файл)",
    )
    parser.add_argument(
        "--script", dest="script_path", metavar="PATH",
        help="путь к стартовому скрипту",
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="работать без GUI, выводя диалог в консоль",
    )
    return parser


def parse_args(argv=None):
    """Разобрать аргументы и вернуть :class:`Config`."""
    namespace = build_parser().parse_args(argv)
    return Config(**vars(namespace))
