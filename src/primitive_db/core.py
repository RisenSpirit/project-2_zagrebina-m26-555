import json

from .decorators import confirm_action, create_cacher, handle_db_errors, log_time
from .utils import load_table_data

VALID_TYPES = {"int", "str", "bool"}
TYPE_MAP = {"int": int, "str": str, "bool": bool}

select_cache = create_cacher()


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу. В начало автоматически добавляется столбец ID:int."""
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')
    if not columns:
        raise ValueError("не указаны столбцы.")

    parsed = [{"name": "ID", "type": "int"}]
    seen = {"ID"}
    for col in columns:
        if col.count(":") != 1:
            raise ValueError(f"некорректный столбец {col}.")
        name, col_type = col.split(":")
        if not name or name in seen:
            raise ValueError(f"некорректное имя столбца {col}.")
        if col_type not in VALID_TYPES:
            raise ValueError(f"неподдерживаемый тип {col_type}. "
                             "Допустимые типы: int, str, bool.")
        seen.add(name)
        parsed.append({"name": name, "type": col_type})

    metadata[table_name] = {"columns": parsed}
    cols_str = ", ".join(f'{c["name"]}:{c["type"]}' for c in parsed)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        raise KeyError(table_name)
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Выводит список всех таблиц."""
    if not metadata:
        print("Таблиц пока нет.")
        return
    for name in metadata:
        print(f"- {name}")


def check_type(value, col_type):
    """Проверяет, что значение соответствует типу столбца."""
    if col_type == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, TYPE_MAP[col_type])


def get_columns(metadata, table_name):
    """Возвращает столбцы таблицы. KeyError, если таблицы нет."""
    if table_name not in metadata:
        raise KeyError(table_name)
    return metadata[table_name]["columns"]


@handle_db_errors
def check_clause(metadata, table_name, clause):
    """Проверяет, что столбцы условия существуют и типы значений верны."""
    types = {c["name"]: c["type"] for c in get_columns(metadata, table_name)}
    for col, value in clause.items():
        if col not in types:
            raise KeyError(col)
        if not check_type(value, types[col]):
            raise ValueError(f"значение {value!r} не подходит для "
                             f"столбца {col}:{types[col]}.")
    return True


def find_rows(table_data, where_clause):
    """Возвращает записи, подходящие под условие."""
    return [row for row in table_data
            if all(row.get(k) == v for k, v in where_clause.items())]


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """
    Добавляет запись в таблицу. ID генерируется автоматически.
    values — список уже разобранных значений без ID.
    """
    data_columns = get_columns(metadata, table_name)[1:]  # все, кроме ID
    if len(values) != len(data_columns):
        raise ValueError(f"ожидается {len(data_columns)} значений, "
                         f"получено {len(values)}.")

    record = {}
    for col, value in zip(data_columns, values):
        if not check_type(value, col["type"]):
            raise ValueError(f"значение {value!r} не подходит для "
                             f'столбца {col["name"]}:{col["type"]}.')
        record[col["name"]] = value

    table_data = load_table_data(table_name)
    new_id = max((row["ID"] for row in table_data), default=0) + 1
    table_data.append({"ID": new_id, **record})
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """
    Возвращает все записи или только подходящие под where_clause.
    Результаты одинаковых запросов к одинаковым данным берутся из кэша.
    """
    key = json.dumps([table_data, where_clause], sort_keys=True,
                     ensure_ascii=False)

    def compute():
        rows = find_rows(table_data, where_clause) if where_clause else table_data
        return [dict(row) for row in rows]

    return select_cache(key, compute)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет поля set_clause в записях, подходящих под where_clause."""
    for row in find_rows(table_data, where_clause):
        row.update(set_clause)
    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    """Удаляет записи, подходящие под where_clause."""
    to_delete = find_rows(table_data, where_clause)
    return [row for row in table_data if row not in to_delete]


@handle_db_errors
def info(metadata, table_name, table_data):
    """Выводит информацию о таблице."""
    columns = get_columns(metadata, table_name)
    cols_str = ", ".join(f'{c["name"]}:{c["type"]}' for c in columns)
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols_str}")
    print(f"Количество записей: {len(table_data)}")
    return True
