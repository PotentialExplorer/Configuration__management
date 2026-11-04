"""Тесты этапа 5: rm и chown (изменения только в памяти)."""

import hashlib
import os
import unittest

from shell_emulator.shell import Shell
from shell_emulator.vfs import load_vfs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEEP_VFS = os.path.join(ROOT, "vfs", "deep.csv")


def file_digest(path):
    """SHA-256 содержимого файла."""
    with open(path, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()


class ModifyTestCase(unittest.TestCase):
    """Базовый класс: сеанс над глубокой VFS."""

    def setUp(self):
        """Создать сеанс."""
        self.shell = Shell(load_vfs(DEEP_VFS, "deep"))

    def run_ok(self, line):
        """Выполнить строку, ожидая успех, и вернуть вывод."""
        result = self.shell.execute(line)
        self.assertFalse(result.error, result.output)
        return result.output

    def run_error(self, line):
        """Выполнить строку, ожидая ошибку, и вернуть результат."""
        result = self.shell.execute(line)
        self.assertTrue(result.error, result.output)
        return result

    def exists(self, path):
        """Проверить существование пути в VFS."""
        return not self.shell.execute(f"ls '{path}'").error


class RmTest(ModifyTestCase):
    """Команда rm."""

    def test_remove_file(self):
        """Удаление файла."""
        self.assertEqual(self.run_ok("rm -v /etc/hostname"),
                         "удалён '/etc/hostname'")
        self.assertFalse(self.exists("/etc/hostname"))

    def test_directory_needs_r(self):
        """Каталог удаляется только с -r."""
        self.assertIn("это каталог", self.run_error("rm /tmp").output)
        self.run_ok("rm -r /tmp")
        self.assertFalse(self.exists("/tmp"))

    def test_force(self):
        """-f подавляет ошибки для несуществующих путей."""
        self.run_error("rm /nope")
        self.run_ok("rm -f /nope")
        self.run_ok("rm -f")

    def test_protected(self):
        """Корень, . и .. не удаляются."""
        self.run_error("rm -r /")
        self.run_error("rm -r .")
        self.run_error("rm -r /home/..")
        self.run_error("rm")

    def test_cwd_inside_removed(self):
        """Если удалён текущий каталог, переходим к родителю."""
        self.run_ok("cd /home/user/projects/emulator/src")
        self.run_ok("rm -r /home/user/projects")
        self.assertEqual(self.shell.cwd.path, "/home/user")

    def test_partial_failure(self):
        """Ошибка одного пути не мешает удалить остальные."""
        result = self.run_error("rm -v /bin/sh /missing /etc/hostname")
        self.assertEqual(result.partial,
                         "удалён '/bin/sh'\nудалён '/etc/hostname'")
        self.assertIn("/missing", result.output)
        self.assertFalse(self.exists("/etc/hostname"))

    def test_source_file_unchanged(self):
        """Изменения не попадают в CSV-файл на диске."""
        before = file_digest(DEEP_VFS)
        self.run_ok("rm -r /home")
        self.assertEqual(file_digest(DEEP_VFS), before)


class ChownTest(ModifyTestCase):
    """Команда chown."""

    def owner(self, path):
        """Владелец узла VFS."""
        return self.shell.resolve(path).owner

    def test_single(self):
        """Смена владельца одного узла не затрагивает потомков."""
        self.run_ok("chown guest /home/user")
        self.assertEqual(self.owner("/home/user"), "guest")
        self.assertEqual(self.owner("/home/user/projects"), "user")

    def test_recursive(self):
        """-R меняет владельца всего поддерева."""
        self.run_ok("chown -R guest /home/user")
        self.assertEqual(
            self.owner("/home/user/projects/emulator/src/main.py"), "guest"
        )

    def test_verbose(self):
        """-v выводит только реальные изменения."""
        output = self.run_ok("chown -v root /etc /etc/hostname /bin/sh")
        self.assertEqual(output, "")
        output = self.run_ok("chown -v user /etc")
        self.assertEqual(output, "владелец '/etc': root -> user")

    def test_ls_shows_owner(self):
        """Новый владелец виден в ls -l."""
        self.run_ok("chown guest /etc/hostname")
        self.assertIn("guest", self.run_ok("ls -l /etc"))

    def test_errors(self):
        """Пропущенные операнды, плохое имя, несуществующий путь."""
        self.run_error("chown")
        self.run_error("chown user")
        self.run_error("chown Bad:Name /tmp")
        self.run_error("chown -q user /tmp")
        result = self.run_error("chown guest /missing /tmp")
        self.assertEqual(self.owner("/tmp"), "guest")
        self.assertTrue(result.output.startswith("chown: /missing"))


if __name__ == "__main__":
    unittest.main()
