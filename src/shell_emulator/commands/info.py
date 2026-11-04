"""Информационные команды: date, cal."""

import calendar
from datetime import timezone

from .base import CommandError

DATE_FORMAT = "%a %b %d %H:%M:%S %Z %Y"
FORMAT_PREFIX = "+"
UTC_FLAG = "-u"
MAX_DATE_ARGS = 2
MIN_MONTH = 1
MAX_MONTH = 12
MIN_YEAR = 1
MAX_YEAR = 9999
ARGS_YEAR = 1
ARGS_MONTH_YEAR = 2


def cmd_date(shell, args):
    """Вывести текущие дату и время.

    ``date [-u] [+ФОРМАТ]``: ``-u`` — время UTC, ``+ФОРМАТ`` —
    формат в стиле ``strftime`` (например, ``+%Y-%m-%d``).
    """
    if len(args) > MAX_DATE_ARGS:
        raise CommandError("date: слишком много аргументов")
    utc = UTC_FLAG in args
    rest = [arg for arg in args if arg != UTC_FLAG]
    fmt = DATE_FORMAT
    for arg in rest:
        if not arg.startswith(FORMAT_PREFIX):
            raise CommandError(f"date: неверный аргумент '{arg}'")
        fmt = arg[len(FORMAT_PREFIX):]
    now = shell.clock(timezone.utc) if utc else shell.clock().astimezone()
    return now.strftime(fmt)


def cmd_cal(shell, args):
    """Вывести календарь.

    ``cal`` — текущий месяц, ``cal ГОД`` — весь год,
    ``cal МЕСЯЦ ГОД`` — указанный месяц.
    """
    printer = calendar.TextCalendar(calendar.SUNDAY)
    if not args:
        today = shell.clock()
        return printer.formatmonth(today.year, today.month).rstrip()
    if len(args) == ARGS_YEAR:
        year = _parse_int("год", args[0], MIN_YEAR, MAX_YEAR)
        return printer.formatyear(year).rstrip()
    if len(args) == ARGS_MONTH_YEAR:
        month = _parse_int("месяц", args[0], MIN_MONTH, MAX_MONTH)
        year = _parse_int("год", args[1], MIN_YEAR, MAX_YEAR)
        return printer.formatmonth(year, month).rstrip()
    raise CommandError("cal: слишком много аргументов")


def _parse_int(what, text, low, high):
    """Преобразовать ``text`` в целое из диапазона ``[low, high]``.

    :raises CommandError: если это не число или оно вне диапазона.
    """
    try:
        value = int(text)
    except ValueError as error:
        raise CommandError(f"cal: {what} '{text}' не число") from error
    if not low <= value <= high:
        raise CommandError(
            f"cal: {what} {value} вне диапазона {low}..{high}"
        )
    return value
