import json

from .constants import (
    COL_NAME_KEY,
    COL_TYPE_KEY,
    COLUMN_SEPARATOR,
    COLUMNS_KEY,
    ID_COLUMN,
    ID_TYPE,
    INT_TYPE,
    TYPE_MAP,
    VALID_TYPES,
)
from .decorators import confirm_action, create_cacher, handle_db_errors, log_time
from .utils import load_table_data

select_cache = create_cacher()


def format_columns(columns):
    """Возвращает строку вида 'ID:int, name:str'."""
    return ", ".join(f'{c["name"]}{COLUMN_SEPARATOR}{c[COL_TYPE_KEY]}' for c in columns)


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу. В начало автоматически добавляется столбец ID:int."""
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')
    if not columns:
        raise ValueError("не указаны столбцы.")

    parsed = [{COL_NAME_KEY: ID_COLUMN, COL_TYPE_KEY: ID_TYPE}]
    seen = {ID_COLUMN}
    for col in columns:
        name, sep, col_type = col.partition(COLUMN_SEPARATOR)
        if not sep or not name or COLUMN_SEPARATOR in col_type or name in seen:
            raise ValueError(f"некорректный столбец {col}.")
        if col_type not in VALID_TYPES:
            raise ValueError(f"неподдерживаемый тип {col_type}. "
                             f"Допустимые типы: {', '.join(VALID_TYPES)}.")
        seen.add(name)
        parsed.append({COL_NAME_KEY: name, COL_TYPE_KEY: col_type})

    metadata[table_name] = {COLUMNS_KEY: parsed}
    print(f'Таблица "{table_name}" успешно создана со столбцами: '
          f"{format_columns(parsed)}")
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    get_columns(metadata, table_name)
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
    """
    Проверяет, что значение соответствует типу столбца.
    """
    if col_type == INT_TYPE:
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, TYPE_MAP[col_type])


def get_columns(metadata, table_name):
    """Возвращает столбцы таблицы. KeyError, если таблицы нет."""
    if table_name not in metadata:
        raise KeyError(table_name)
    return metadata[table_name][COLUMNS_KEY]


@handle_db_errors
def check_clause(metadata, table_name, clause):
    """Проверяет, что столбцы условия существуют и типы значений верны."""
    columns = get_columns(metadata, table_name)
    types = {c[COL_NAME_KEY]: c[COL_TYPE_KEY] for c in columns}
    for col, value in clause.items():
        if col not in types:
            raise KeyError(col)
        if not check_type(value, types[col]):
            raise ValueError(f"значение {value!r} не подходит для "
                             f"столбца {col}{COLUMN_SEPARATOR}{types[col]}.")
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
        if not check_type(value, col[COL_TYPE_KEY]):
            raise ValueError(f"значение {value!r} не подходит для столбца "
                             f'{col[COL_NAME_KEY]}{COLUMN_SEPARATOR}{col[COL_TYPE_KEY]}.')
        record[col[COL_NAME_KEY]] = value

    table_data = load_table_data(table_name)
    new_id = max((row[ID_COLUMN] for row in table_data), default=0) + 1
    table_data.append({ID_COLUMN: new_id, **record})
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
        """Выполняет выборку без кэша."""
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
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {format_columns(columns)}")
    print(f"Количество записей: {len(table_data)}")
    return True
