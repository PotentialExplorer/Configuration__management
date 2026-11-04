"""Тесты этапа 4: ls, cd, date, tree, cal."""

import os
import unittest
from datetime import datetime, timezone

from shell_emulator.shell import Shell
from shell_emulator.vfs import load_vfs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEEP_VFS = os.path.join(ROOT, "vfs", "deep.csv")
FIXED_NOW = datetime(2024, 2, 29, 13, 45, 30, tzinfo=timezone.utc)


def fixed_clock(tz=None):
    """Часы с фиксированным временем для воспроизводимых тестов."""
    return FIXED_NOW if tz is None else FIXED_NOW.astimezone(tz)


class CommandTestCase(unittest.TestCase):
    """Базовый класс: сеанс над глубокой VFS с фиксированными часами."""

    def setUp(self):
        """Создать сеанс."""
        self.shell = Shell(load_vfs(DEEP_VFS, "deep"))
        self.shell.clock = fixed_clock

    def run_ok(self, line):
        """Выполнить строку, ожидая успех, и вернуть вывод."""
        result = self.shell.execute(line)
        self.assertFalse(result.error, result.output)
        return result.output

    def run_error(self, line):
        """Выполнить строку, ожидая ошибку, и вернуть сообщение."""
        result = self.shell.execute(line)
        self.assertTrue(result.error, result.output)
        return result.output


class LsTest(CommandTestCase):
    """Команда ls."""

    def test_root(self):
        """Содержимое корня по алфавиту."""
        self.assertEqual(self.run_ok("ls"), "bin  etc  home  tmp")

    def test_long(self):
        """Подробный формат содержит права, владельца и размер."""
        line = self.run_ok("ls -l /etc")
        self.assertEqual(line.split(), ["-rw-r--r--", "root", "9",
                                        "hostname"])

    def test_all(self):
        """Ключ -a добавляет . и .."""
        self.assertTrue(self.run_ok("ls -a /tmp").startswith(".  .."))

    def test_quoted_path(self):
        """Путь с пробелом в кавычках."""
        output = self.run_ok('ls "/home/user/My Documents"')
        self.assertEqual(output, "report.txt")

    def test_several_paths(self):
        """Несколько каталогов выводятся с заголовками."""
        self.assertEqual(self.run_ok("ls /bin /etc"),
                         "/bin:\nsh\n\n/etc:\nhostname")

    def test_errors(self):
        """Несуществующий путь и неизвестный ключ."""
        self.assertIn("нет такого", self.run_error("ls /nope"))
        self.assertIn("неверный ключ", self.run_error("ls -q"))


class CdTest(CommandTestCase):
    """Команда cd."""

    def test_absolute_and_relative(self):
        """Абсолютные, относительные пути и .."""
        self.run_ok("cd /home/user/projects")
        self.run_ok("cd emulator/src")
        self.run_ok("cd ../..")
        self.assertEqual(self.shell.cwd.path, "/home/user/projects")

    def test_home(self):
        """cd без аргументов и cd ~ ведут в домашний каталог."""
        self.run_ok("cd")
        self.assertEqual(self.shell.cwd.path, "/home/user")
        self.run_ok("cd /")
        self.run_ok("cd ~/projects")
        self.assertEqual(self.shell.cwd.path, "/home/user/projects")

    def test_prompt_shows_cwd(self):
        """Приглашение показывает текущий каталог."""
        self.run_ok("cd /etc")
        self.assertEqual(self.shell.prompt(), "user@deep:/etc$ ")

    def test_errors(self):
        """Файл, несуществующий путь, лишние аргументы."""
        self.assertIn("не каталог", self.run_error("cd /etc/hostname"))
        self.assertEqual(self.run_error("cd /x"),
                         "cd: /x: нет такого файла или каталога")
        self.run_error("cd a b")
        self.assertEqual(self.shell.cwd.path, "/")


class DateTest(CommandTestCase):
    """Команда date."""

    def test_utc(self):
        """date -u выводит время UTC в стандартном формате."""
        self.assertEqual(self.run_ok("date -u"),
                         "Thu Feb 29 13:45:30 UTC 2024")

    def test_format(self):
        """Пользовательский формат."""
        self.assertEqual(self.run_ok("date -u +%Y-%m-%d"), "2024-02-29")

    def test_errors(self):
        """Неверный аргумент."""
        self.assertIn("неверный аргумент", self.run_error("date now"))


class TreeTest(CommandTestCase):
    """Команда tree."""

    def test_subtree(self):
        """Дерево каталога и итоговая статистика."""
        output = self.run_ok("tree /etc")
        self.assertEqual(output,
                         "/etc\n└── hostname\n\nкаталогов: 0, файлов: 1")

    def test_dirs_only(self):
        """Ключ -d скрывает файлы."""
        output = self.run_ok("tree -d /home")
        self.assertNotIn("todo.txt", output)
        self.assertIn("каталогов: 6, файлов: 0", output)

    def test_errors(self):
        """Файл вместо каталога и лишние аргументы."""
        self.run_error("tree /etc/hostname")
        self.run_error("tree / /etc")


class CalTest(CommandTestCase):
    """Команда cal."""

    def test_current_month(self):
        """Без аргументов — текущий месяц."""
        self.assertIn("February 2024", self.run_ok("cal"))

    def test_month_year(self):
        """Високосный февраль содержит 29-е число."""
        self.assertTrue(self.run_ok("cal 2 2024").endswith("29"))

    def test_year(self):
        """Весь год содержит все месяцы."""
        output = self.run_ok("cal 2026")
        self.assertIn("January", output)
        self.assertIn("December", output)

    def test_errors(self):
        """Неверный месяц, не число, лишние аргументы."""
        self.assertIn("вне диапазона", self.run_error("cal 13 2026"))
        self.assertIn("не число", self.run_error("cal abc"))
        self.run_error("cal 1 2 3")


if __name__ == "__main__":
    unittest.main()
