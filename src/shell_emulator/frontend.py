"""Общая логика интерфейсов эмулятора и консольный интерфейс."""

from .script import ScriptError, read_script, run_script


class Frontend:
    """Базовый интерфейс: показ ввода, вывода и запуск скриптов.

    Наследники реализуют :meth:`write`, :meth:`on_stop`
    и :meth:`mainloop`.
    """

    def __init__(self, shell):
        """Связать интерфейс с сеансом ``shell``."""
        self.shell = shell

    def write(self, text, tag=None):
        """Вывести ``text``; ``tag`` — вид сообщения (error, prompt...)."""
        raise NotImplementedError

    def on_stop(self):
        """Реакция интерфейса на завершение сеанса."""

    def mainloop(self):
        """Запустить интерактивный режим."""
        raise NotImplementedError

    def run_line(self, line):
        """Показать строку как ввод, выполнить её и вывести результат."""
        self.write(self.shell.prompt() + line, "prompt")
        result = self.shell.execute(line)
        self.write(result.partial)
        self.write(result.output, "error" if result.error else None)
        if result.stop:
            self.on_stop()
        return result

    def run_startup_script(self, path):
        """Выполнить стартовый скрипт, имитируя диалог с пользователем.

        :return: число ошибочных строк или ``None``, если скрипт
            не удалось прочитать.
        """
        try:
            lines = read_script(path)
        except ScriptError as error:
            self.write(f"[script] ошибка: {error}", "error")
            return None
        return run_script(lines, self.run_line, self._report)

    def _report(self, text):
        """Вывести служебное сообщение скрипта."""
        tag = "error" if "ошибка" in text else "info"
        self.write(text, tag)


class ConsoleFrontend(Frontend):
    """Консольный интерфейс (режим ``--headless``)."""

    def write(self, text, tag=None):
        """Напечатать ``text`` в стандартный вывод."""
        if text:
            print(text, flush=True)

    def mainloop(self):
        """Читать команды со стандартного ввода до EOF или exit."""
        while self.shell.running:
            try:
                line = input(self.shell.prompt())
            except EOFError:
                break
            result = self.shell.execute(line)
            self.write(result.partial)
            self.write(result.output)
