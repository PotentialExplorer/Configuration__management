"""Выполнение стартовых скриптов эмулятора."""

COMMENT_PREFIX = "#"


class ScriptError(Exception):
    """Стартовый скрипт не удалось прочитать."""


def read_script(path):
    """Прочитать стартовый скрипт и вернуть список строк.

    :raises ScriptError: если файл не найден или не читается.
    """
    try:
        with open(path, encoding="utf-8") as file:
            return file.read().splitlines()
    except FileNotFoundError as error:
        raise ScriptError(f"скрипт '{path}' не найден") from error
    except OSError as error:
        raise ScriptError(
            f"не удалось открыть скрипт '{path}': {error.strerror}"
        ) from error
    except UnicodeDecodeError as error:
        raise ScriptError(
            f"скрипт '{path}' не в кодировке UTF-8"
        ) from error


def run_script(lines, run_line, report):
    """Последовательно выполнить строки скрипта.

    Пустые строки и строки-комментарии (``#``) пропускаются. Ошибочные
    строки не прерывают скрипт: о них сообщается через ``report``.

    :param lines: строки скрипта.
    :param run_line: функция, которая показывает строку как ввод,
        выполняет её и возвращает ``CommandResult``; если у результата
        ``stop`` истинно (была выполнена ``exit``), скрипт прерывается.
    :param report: функция ``report(text)`` для сообщений об ошибках.
    :return: число строк, завершившихся ошибкой.
    """
    errors = 0
    for number, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith(COMMENT_PREFIX):
            continue
        result = run_line(line)
        if result.error:
            errors += 1
            report(f"[script] ошибка в строке {number}: {line}")
        if result.stop:
            break
    report(f"[script] выполнение завершено, ошибок: {errors}")
    return errors
