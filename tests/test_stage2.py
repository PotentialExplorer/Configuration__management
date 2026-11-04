"""Тесты этапа 2: параметры командной строки и стартовый скрипт."""

import os
import tempfile
import unittest

from shell_emulator.config import parse_args
from shell_emulator.frontend import Frontend
from shell_emulator.shell import Shell


class RecordingFrontend(Frontend):
    """Интерфейс, запоминающий весь вывод (для тестов)."""

    def __init__(self, shell):
        """Создать интерфейс с пустым журналом вывода."""
        super().__init__(shell)
        self.lines = []

    def write(self, text, tag=None):
        """Сохранить строку вывода вместе с тегом."""
        if text:
            self.lines.append((tag, text))

    def mainloop(self):
        """Интерактивный режим в тестах не нужен."""


def write_temp(text):
    """Записать ``text`` во временный файл и вернуть путь к нему."""
    handle, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(handle, "w", encoding="utf-8") as file:
        file.write(text)
    return path


class ConfigTest(unittest.TestCase):
    """Проверки разбора параметров запуска."""

    def test_defaults(self):
        """Без параметров пути не заданы, имя VFS по умолчанию."""
        config = parse_args([])
        self.assertIsNone(config.vfs_path)
        self.assertIsNone(config.script_path)
        self.assertEqual(config.vfs_name, "default")

    def test_all_params(self):
        """Все параметры попадают в конфигурацию и отладочный вывод."""
        config = parse_args(["--vfs", "a/b/my.csv", "--script", "s.txt"])
        self.assertEqual(config.vfs_name, "my")
        text = "\n".join(config.describe())
        self.assertIn("a/b/my.csv", text)
        self.assertIn("s.txt", text)


class StartupScriptTest(unittest.TestCase):
    """Проверки выполнения стартового скрипта."""

    def run_text(self, text):
        """Выполнить скрипт ``text`` и вернуть (интерфейс, ошибки)."""
        path = write_temp(text)
        self.addCleanup(os.remove, path)
        frontend = RecordingFrontend(Shell())
        return frontend, frontend.run_startup_script(path)

    def test_echo_input_and_output(self):
        """Скрипт показывает и ввод, и вывод."""
        frontend, errors = self.run_text("ls '/home'\n")
        self.assertEqual(errors, 0)
        self.assertIn(("prompt", "user@default:/$ ls '/home'"), frontend.lines)
        self.assertIn((None, "user"), frontend.lines)

    def test_errors_are_skipped(self):
        """Ошибочные строки пропускаются, выполнение продолжается."""
        frontend, errors = self.run_text("bad\n# comment\n\nls /tmp /home\n")
        self.assertEqual(errors, 1)
        texts = [text for _, text in frontend.lines]
        self.assertIn("[script] ошибка в строке 1: bad", texts)
        self.assertIn("/tmp:\n\n/home:\nuser", texts)

    def test_exit_stops_script(self):
        """После exit оставшиеся строки не выполняются."""
        frontend, _ = self.run_text("exit\ncd /home\n")
        self.assertEqual(frontend.shell.cwd.path, "/")
        self.assertFalse(frontend.shell.running)

    def test_missing_script(self):
        """Отсутствующий скрипт — сообщение об ошибке."""
        frontend = RecordingFrontend(Shell())
        self.assertIsNone(frontend.run_startup_script("/no/such/file"))
        self.assertEqual(frontend.lines[0][0], "error")


if __name__ == "__main__":
    unittest.main()
