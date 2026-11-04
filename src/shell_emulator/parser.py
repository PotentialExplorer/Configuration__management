"""Разбор командной строки эмулятора."""

import shlex


class ParseError(Exception):
    """Ошибка разбора командной строки (например, незакрытая кавычка)."""


def parse_line(line):
    """Разбить строку на имя команды и список аргументов.

    Аргументы в одинарных и двойных кавычках считаются одним токеном,
    кавычки при этом удаляются, экранирование через ``\\`` сохраняется.

    :param line: строка, введённая пользователем.
    :return: кортеж ``(имя_команды, аргументы)``; для пустой строки
        возвращается ``(None, [])``.
    :raises ParseError: если строка не может быть разобрана.
    """
    try:
        tokens = shlex.split(line, posix=True)
    except ValueError as error:
        raise ParseError(_translate(str(error))) from error
    if not tokens:
        return None, []
    return tokens[0], tokens[1:]


def _translate(message):
    """Перевести сообщение об ошибке ``shlex`` на русский язык."""
    known = {
        "No closing quotation": "незакрытая кавычка",
        "No escaped character": "нет символа после '\\'",
    }
    return "ошибка разбора: " + known.get(message, message)
