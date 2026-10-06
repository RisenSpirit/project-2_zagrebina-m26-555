import json
import os

from .constants import (
    DATA_DIR,
    DATA_FILE_EXTENSION,
    ENCODING,
    JSON_INDENT,
    META_FILE,
    READ_MODE,
    WRITE_MODE,
)


def load_metadata(filepath=META_FILE):
    """Загружает метаданные из JSON-файла. Если файла нет — возвращает {}."""
    try:
        with open(filepath, READ_MODE, encoding=ENCODING) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(data, filepath=META_FILE):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, WRITE_MODE, encoding=ENCODING) as f:
        json.dump(data, f, ensure_ascii=False, indent=JSON_INDENT)


def get_table_path(table_name):
    """Возвращает путь к файлу с данными таблицы: data/<имя>.json."""
    return os.path.join(DATA_DIR, f"{table_name}{DATA_FILE_EXTENSION}")


def load_table_data(table_name):
    """Загружает записи таблицы. Если файла нет — возвращает []."""
    try:
        with open(get_table_path(table_name), READ_MODE, encoding=ENCODING) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы, при необходимости создаёт директорию data/."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_table_path(table_name), WRITE_MODE, encoding=ENCODING) as f:
        json.dump(data, f, ensure_ascii=False, indent=JSON_INDENT)


def delete_table_data(table_name):
    """Удаляет файл с данными таблицы, если он существует."""
    path = get_table_path(table_name)
    if os.path.exists(path):
        os.remove(path)
