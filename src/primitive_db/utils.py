import json
import os

META_FILE = "db_meta.json"
DATA_DIR = "data"


def load_metadata(filepath=META_FILE):
    """Загружает метаданные из JSON-файла. Если файла нет — возвращает {}."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(data, filepath=META_FILE):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def _table_path(table_name):
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name):
    """Загружает записи таблицы из data/<имя>.json. Если файла нет — []."""
    try:
        with open(_table_path(table_name), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в data/<имя>.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_table_path(table_name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    """Удаляет файл с данными таблицы, если он есть."""
    try:
        os.remove(_table_path(table_name))
    except FileNotFoundError:
        pass
