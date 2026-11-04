"""Графический интерфейс эмулятора на базе tkinter."""

import tkinter as tk
from tkinter import scrolledtext

WINDOW_SIZE = "800x500"
FONT = ("Courier New", 11)
CLOSE_DELAY_MS = 300


class ShellWindow:
    """Окно терминала: область вывода и строка ввода."""

    def __init__(self, shell):
        """Создать окно для сеанса ``shell``."""
        self.shell = shell
        self.root = tk.Tk()
        self.root.title(f"Эмулятор оболочки — VFS: {shell.vfs_name}")
        self.root.geometry(WINDOW_SIZE)
        self._build_widgets()

    def _build_widgets(self):
        """Создать и разместить виджеты окна."""
        self.output = scrolledtext.ScrolledText(
            self.root, font=FONT, state=tk.DISABLED,
            bg="black", fg="#d0d0d0",
        )
        self.output.tag_config("error", foreground="#ff6060")
        self.output.tag_config("prompt", foreground="#60ff60")
        self.output.pack(fill=tk.BOTH, expand=True)
        bottom = tk.Frame(self.root)
        bottom.pack(fill=tk.X)
        self.prompt_label = tk.Label(bottom, font=FONT)
        self.prompt_label.pack(side=tk.LEFT)
        self.entry = tk.Entry(bottom, font=FONT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()
        self._update_prompt()

    def _update_prompt(self):
        """Обновить приглашение рядом со строкой ввода."""
        self.prompt_label.config(text=self.shell.prompt())

    def write(self, text, tag=None):
        """Добавить ``text`` в область вывода с тегом оформления."""
        if not text:
            return
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n", tag)
        self.output.config(state=tk.DISABLED)
        self.output.see(tk.END)

    def run_line(self, line):
        """Показать строку как ввод, выполнить её и вывести результат.

        :return: :class:`~shell_emulator.shell.CommandResult`.
        """
        self.write(self.shell.prompt() + line, "prompt")
        result = self.shell.execute(line)
        self.write(result.output, "error" if result.error else None)
        self._update_prompt()
        if not self.shell.running:
            self.root.after(CLOSE_DELAY_MS, self.root.destroy)
        return result

    def _on_enter(self, _event):
        """Обработать нажатие Enter в строке ввода."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.run_line(line)

    def mainloop(self):
        """Запустить цикл обработки событий окна."""
        self.root.mainloop()
