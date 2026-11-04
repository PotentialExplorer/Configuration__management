"""Тесты этапа 1: парсер, заглушки ls/cd, exit, ошибки."""

import unittest

from shell_emulator.parser import ParseError, parse_line
from shell_emulator.shell import Shell


class ParserTest(unittest.TestCase):
    """Проверки разбора командной строки."""

    def test_simple(self):
        """Строка без кавычек делится по пробелам."""
        self.assertEqual(parse_line("ls -l /home"), ("ls", ["-l", "/home"]))

    def test_double_quotes(self):
        """Аргумент в двойных кавычках — один токен."""
        self.assertEqual(
            parse_line('cd "My Documents"'), ("cd", ["My Documents"])
        )

    def test_single_quotes(self):
        """Аргумент в одинарных кавычках — один токен."""
        self.assertEqual(parse_line("ls 'a b' c"), ("ls", ["a b", "c"]))

    def test_glued_quotes(self):
        """Кавычки внутри слова склеиваются с ним."""
        self.assertEqual(parse_line('ls ab"c d"e'), ("ls", ["abc de"]))

    def test_empty(self):
        """Пустая строка не содержит команды."""
        self.assertEqual(parse_line("   "), (None, []))

    def test_unclosed_quote(self):
        """Незакрытая кавычка приводит к ошибке разбора."""
        with self.assertRaises(ParseError):
            parse_line('ls "abc')


class ShellStage1Test(unittest.TestCase):
    """Проверки выполнения команд этапа 1."""

    def setUp(self):
        """Создать новый сеанс для каждого теста."""
        self.shell = Shell()

    def test_unknown_command(self):
        """Неизвестная команда — ошибка."""
        result = self.shell.execute("foo bar")
        self.assertTrue(result.error)
        self.assertIn("команда не найдена", result.output)

    def test_parse_error(self):
        """Ошибка разбора сообщается пользователю."""
        result = self.shell.execute("cd 'abc")
        self.assertTrue(result.error)
        self.assertIn("незакрытая кавычка", result.output)

    def test_exit(self):
        """exit останавливает сеанс."""
        self.shell.execute("exit 3")
        self.assertFalse(self.shell.running)
        self.assertEqual(self.shell.exit_code, 3)

    def test_exit_bad_arg(self):
        """exit с нечисловым аргументом — ошибка, сеанс продолжается."""
        result = self.shell.execute("exit abc")
        self.assertTrue(result.error)
        self.assertTrue(self.shell.running)

    def test_empty_line(self):
        """Пустая строка ничего не выводит."""
        result = self.shell.execute("")
        self.assertFalse(result.error)
        self.assertEqual(result.output, "")


if __name__ == "__main__":
    unittest.main()
