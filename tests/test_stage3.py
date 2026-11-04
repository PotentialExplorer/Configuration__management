"""Тесты этапа 3: загрузка VFS из CSV и разрешение путей."""

import base64
import os
import tempfile
import unittest

from shell_emulator.vfs import VfsError, create_default_vfs, load_vfs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VFS_DIR = os.path.join(ROOT, "vfs")
HEADER = "path,type,owner,content\n"


def vfs_path(name):
    """Путь к тестовой VFS из каталога ``vfs``."""
    return os.path.join(VFS_DIR, name)


def load_text(text):
    """Загрузить VFS из CSV-текста через временный файл."""
    handle, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(handle, "w", encoding="utf-8") as file:
        file.write(text)
    try:
        return load_vfs(path)
    finally:
        os.remove(path)


class LoadVfsTest(unittest.TestCase):
    """Проверки загрузки VFS."""

    def test_minimal(self):
        """Минимальная VFS содержит только корень."""
        vfs = load_vfs(vfs_path("minimal.csv"), "minimal")
        self.assertEqual(vfs.stats(), (1, 0, 0))
        self.assertEqual(vfs.name, "minimal")

    def test_binary_file(self):
        """Двоичное содержимое декодируется из base64."""
        vfs = load_vfs(vfs_path("few_files.csv"))
        logo = vfs.resolve("/logo.png")
        self.assertTrue(logo.data.startswith(b"\x89PNG"))

    def test_deep_tree(self):
        """Вложенность задаётся путём, промежуточные каталоги неявные."""
        vfs = load_vfs(vfs_path("deep.csv"))
        node = vfs.resolve("/home/user/projects/emulator/src/main.py")
        self.assertEqual(node.data, b"print('hi')\n")
        self.assertEqual(node.parent.owner, "user")

    def test_file_not_found(self):
        """Отсутствующий файл — ошибка загрузки."""
        with self.assertRaisesRegex(VfsError, "не найден"):
            load_vfs(vfs_path("no_such.csv"))

    def test_bad_header(self):
        """Неверный заголовок — ошибка формата."""
        with self.assertRaisesRegex(VfsError, "заголовок"):
            load_vfs(vfs_path("broken_header.csv"))

    def test_bad_base64(self):
        """Некорректный base64 — ошибка формата."""
        with self.assertRaisesRegex(VfsError, "base64"):
            load_vfs(vfs_path("broken_base64.csv"))

    def test_file_as_parent(self):
        """Файл не может быть родителем."""
        with self.assertRaisesRegex(VfsError, "не является каталогом"):
            load_vfs(vfs_path("broken_tree.csv"))

    def test_relative_path(self):
        """Пути в CSV должны быть абсолютными."""
        with self.assertRaisesRegex(VfsError, "абсолютным"):
            load_text(HEADER + "a,dir,root,\n")

    def test_duplicate(self):
        """Повторяющийся путь — ошибка."""
        with self.assertRaisesRegex(VfsError, "повторяющийся"):
            load_text(HEADER + "/a,dir,root,\n/a,dir,root,\n")

    def test_unknown_type(self):
        """Неизвестный тип узла — ошибка."""
        with self.assertRaisesRegex(VfsError, "тип"):
            load_text(HEADER + "/a,link,root,\n")

    def test_source_not_modified(self):
        """Загрузка не изменяет файл на диске."""
        path = vfs_path("deep.csv")
        with open(path, "rb") as file:
            before = file.read()
        vfs = load_vfs(path)
        vfs.root.remove("tmp")
        with open(path, "rb") as file:
            self.assertEqual(file.read(), before)

    def test_content_round_trip(self):
        """Содержимое совпадает с исходными байтами."""
        data = bytes(range(256))
        encoded = base64.b64encode(data).decode()
        vfs = load_text(HEADER + f"/x.bin,file,root,{encoded}\n")
        self.assertEqual(vfs.resolve("/x.bin").data, data)


class ResolveTest(unittest.TestCase):
    """Проверки разрешения путей."""

    def setUp(self):
        """Загрузить глубокую VFS."""
        self.vfs = load_vfs(vfs_path("deep.csv"))

    def test_relative_and_parent(self):
        """Относительные пути, ``.`` и ``..``."""
        home = self.vfs.resolve("/home")
        node = self.vfs.resolve("user/../guest/./todo.txt", home)
        self.assertEqual(node.path, "/home/guest/todo.txt")

    def test_parent_of_root(self):
        """``..`` от корня остаётся в корне."""
        self.assertIs(self.vfs.resolve("/../.."), self.vfs.root)

    def test_missing(self):
        """Несуществующий путь — ошибка."""
        with self.assertRaises(VfsError):
            self.vfs.resolve("/home/nobody")

    def test_default_vfs(self):
        """VFS по умолчанию создаётся в памяти."""
        vfs = create_default_vfs()
        self.assertIsNone(vfs.source)
        self.assertTrue(vfs.resolve("/home/user").is_dir)


if __name__ == "__main__":
    unittest.main()
