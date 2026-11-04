"""Виртуальная файловая система (VFS) в памяти, загружаемая из CSV.

Формат CSV (первая строка — заголовок)::

    path,type,owner,content
    /home,dir,user,
    /home/user/hello.txt,file,user,SGVsbG8K

* ``path`` — абсолютный путь; вложенность задаётся через ``/``.
  Недостающие родительские каталоги создаются автоматически.
* ``type`` — ``dir`` или ``file``.
* ``owner`` — владелец (пусто — ``root``).
* ``content`` — содержимое файла в base64 (для каталогов пусто).

Файл на диске только читается: все изменения делаются в памяти.
"""

import base64
import binascii
import csv

CSV_FIELDS = ["path", "type", "owner", "content"]
TYPE_DIR = "dir"
TYPE_FILE = "file"
DEFAULT_OWNER = "root"
DEFAULT_NAME = "default"
SEP = "/"
PARENT = ".."
CURRENT = "."


class VfsError(Exception):
    """Ошибка загрузки VFS или обращения к ней."""


class Node:
    """Узел VFS: общий предок файлов и каталогов."""

    is_dir = False

    def __init__(self, name, owner=DEFAULT_OWNER, parent=None):
        """Создать узел с именем ``name`` и владельцем ``owner``."""
        self.name = name
        self.owner = owner
        self.parent = parent

    @property
    def path(self):
        """Абсолютный путь к узлу."""
        if self.parent is None:
            return SEP
        parent_path = self.parent.path.rstrip(SEP)
        return f"{parent_path}{SEP}{self.name}"


class Directory(Node):
    """Каталог VFS."""

    is_dir = True

    def __init__(self, name, owner=DEFAULT_OWNER, parent=None):
        """Создать пустой каталог."""
        super().__init__(name, owner, parent)
        self.children = {}
        self.implicit = False

    def add(self, node):
        """Добавить дочерний узел и вернуть его."""
        node.parent = self
        self.children[node.name] = node
        return node

    def remove(self, name):
        """Удалить дочерний узел ``name``."""
        node = self.children.pop(name)
        node.parent = None

    def sorted_children(self):
        """Дочерние узлы, отсортированные по имени."""
        return [self.children[key] for key in sorted(self.children)]


class File(Node):
    """Файл VFS с двоичным содержимым."""

    def __init__(self, name, data=b"", owner=DEFAULT_OWNER, parent=None):
        """Создать файл с содержимым ``data``."""
        super().__init__(name, owner, parent)
        self.data = data

    @property
    def size(self):
        """Размер файла в байтах."""
        return len(self.data)


class Vfs:
    """Дерево VFS с корневым каталогом и разрешением путей."""

    def __init__(self, name=DEFAULT_NAME, source=None):
        """Создать пустую VFS с именем ``name``."""
        self.name = name
        self.source = source
        self.root = Directory("")

    def resolve(self, path, cwd=None):
        """Найти узел по абсолютному или относительному пути.

        Поддерживаются ``.`` и ``..``.

        :raises VfsError: если путь не существует.
        """
        node = cwd if cwd is not None else self.root
        if path.startswith(SEP):
            node = self.root
        for part in _split(path):
            node = self._step(node, part, path)
        return node

    def _step(self, node, part, path):
        """Сделать один шаг разрешения пути от ``node``."""
        if part == CURRENT:
            return node
        if part == PARENT:
            return node.parent or self.root
        if not node.is_dir or part not in node.children:
            raise VfsError(f"{path}: нет такого файла или каталога")
        return node.children[part]

    def walk(self, start=None):
        """Обойти все узлы поддерева в глубину (включая ``start``)."""
        stack = [start or self.root]
        while stack:
            node = stack.pop()
            yield node
            if node.is_dir:
                stack.extend(reversed(node.sorted_children()))

    def stats(self):
        """Вернуть кортеж (число каталогов, число файлов, байт)."""
        dirs = files = total = 0
        for node in self.walk():
            if node.is_dir:
                dirs += 1
            else:
                files += 1
                total += node.size
        return dirs, files, total


def _split(path):
    """Разбить путь на непустые компоненты."""
    return [part for part in path.split(SEP) if part]


def create_default_vfs():
    """Создать VFS по умолчанию в памяти (если путь не задан)."""
    vfs = Vfs(DEFAULT_NAME)
    home = vfs.root.add(Directory("home"))
    user = home.add(Directory("user", owner="user"))
    user.add(File("readme.txt", b"Default VFS\n", owner="user"))
    vfs.root.add(Directory("tmp"))
    return vfs


def load_vfs(path, name=DEFAULT_NAME):
    """Загрузить VFS из CSV-файла ``path``.

    :raises VfsError: файл не найден или имеет неверный формат.
    """
    vfs = Vfs(name, source=path)
    try:
        with open(path, encoding="utf-8", newline="") as file:
            _fill(vfs, csv.DictReader(file))
    except FileNotFoundError as error:
        raise VfsError(f"файл VFS '{path}' не найден") from error
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        raise VfsError(f"не удалось прочитать VFS '{path}': {error}") \
            from error
    return vfs


def _fill(vfs, reader):
    """Заполнить ``vfs`` строками из ``csv.DictReader``."""
    if reader.fieldnames != CSV_FIELDS:
        raise VfsError(
            "неверный формат VFS: ожидается заголовок "
            + ",".join(CSV_FIELDS)
        )
    for row in reader:
        try:
            _add_row(vfs, row)
        except VfsError as error:
            raise VfsError(
                f"неверный формат VFS, строка {reader.line_num}: {error}"
            ) from error


def _add_row(vfs, row):
    """Добавить в VFS узел, описанный строкой CSV."""
    path = (row.get("path") or "").strip()
    kind = (row.get("type") or "").strip()
    owner = (row.get("owner") or "").strip() or DEFAULT_OWNER
    if not path.startswith(SEP):
        raise VfsError(f"путь '{path}' должен быть абсолютным")
    if kind not in (TYPE_DIR, TYPE_FILE):
        raise VfsError(f"неизвестный тип '{kind}'")
    parts = _split(path)
    if not parts:
        _set_root(vfs, kind, owner)
        return
    parent = _ensure_dirs(vfs, parts[:-1])
    existing = parent.children.get(parts[-1])
    if existing is not None:
        _redefine(existing, kind, owner, path)
        return
    parent.add(_make_node(parts[-1], kind, owner, row.get("content")))


def _redefine(node, kind, owner, path):
    """Уточнить неявно созданный каталог явной строкой CSV."""
    if not (node.is_dir and node.implicit and kind == TYPE_DIR):
        raise VfsError(f"повторяющийся путь '{path}'")
    node.owner = owner
    node.implicit = False


def _set_root(vfs, kind, owner):
    """Обработать строку CSV, описывающую корень ``/``."""
    if kind != TYPE_DIR:
        raise VfsError("корень VFS должен быть каталогом")
    vfs.root.owner = owner


def _ensure_dirs(vfs, parts):
    """Вернуть каталог по компонентам пути, создавая недостающие."""
    node = vfs.root
    for part in parts:
        child = node.children.get(part)
        if child is None:
            child = node.add(Directory(part, owner=node.owner))
            child.implicit = True
        if not child.is_dir:
            raise VfsError(f"'{child.path}' не является каталогом")
        node = child
    return node


def _make_node(name, kind, owner, content):
    """Создать файл или каталог по данным строки CSV."""
    content = (content or "").strip()
    if kind == TYPE_DIR:
        if content:
            raise VfsError(f"у каталога '{name}' не может быть содержимого")
        return Directory(name, owner)
    try:
        data = base64.b64decode(content, validate=True)
    except (binascii.Error, ValueError) as error:
        raise VfsError(f"некорректный base64 у файла '{name}'") from error
    return File(name, data, owner)
