import re
import shlex

import prompt
from prettytable import PrettyTable

from .core import (
    check_clause,
    create_table,
    delete,
    drop_table,
    find_rows,
    get_columns,
    info,
    insert,
    list_tables,
    select,
    update,
)
from .decorators import handle_db_errors
from .parser import parse_set, parse_values, parse_where
from .utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

INSERT_RE = re.compile(r"^insert\s+into\s+(\w+)\s+values\s*\((.*)\)\s*$", re.I)
SELECT_RE = re.compile(r"^select\s+from\s+(\w+)(?:\s+where\s+(.+))?$", re.I)
UPDATE_RE = re.compile(r"^update\s+(\w+)\s+set\s+(.+?)\s+where\s+(.+)$", re.I)
DELETE_RE = re.compile(r"^delete\s+from\s+(\w+)\s+where\s+(.+)$", re.I)
INFO_RE = re.compile(r"^info\s+(\w+)$", re.I)


def print_help():
    """Выводит справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. "
          "- создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) "
          "- создать запись.")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> "
          "- прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
          "where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> "
          "- удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_rows(metadata, table_name, rows):
    """Выводит записи в виде таблицы PrettyTable."""
    names = [c["name"] for c in metadata[table_name]["columns"]]
    table = PrettyTable()
    table.field_names = names
    for row in rows:
        table.add_row([row.get(n) for n in names])
    print(table)


@handle_db_errors
def handle_create_table(metadata, args):
    if not args:
        raise ValueError("не указано имя таблицы.")
    table_name = args[0]
    if create_table(metadata, table_name, args[1:]) is None:
        return
    save_metadata(metadata)
    save_table_data(table_name, [])


@handle_db_errors
def handle_drop_table(metadata, args):
    if len(args) != 1:
        raise ValueError("укажите одно имя таблицы.")
    table_name = args[0]
    get_columns(metadata, table_name)  # KeyError, если таблицы нет
    if drop_table(metadata, table_name) is None:
        return  # операция отменена
    save_metadata(metadata)
    delete_table_data(table_name)


@handle_db_errors
def handle_insert(metadata, match):
    table_name, values = match.group(1), parse_values(match.group(2))
    table_data = insert(metadata, table_name, values)
    if table_data is not None:
        save_table_data(table_name, table_data)


@handle_db_errors
def handle_select(metadata, match):
    table_name = match.group(1)
    get_columns(metadata, table_name)
    where = parse_where(match.group(2)) if match.group(2) else None
    if where and not check_clause(metadata, table_name, where):
        return
    rows = select(load_table_data(table_name), where)
    if rows is None:
        return
    if not rows:
        print("Записи не найдены.")
        return
    print_rows(metadata, table_name, rows)


@handle_db_errors
def handle_update(metadata, match):
    table_name = match.group(1)
    get_columns(metadata, table_name)
    set_clause, where = parse_set(match.group(2)), parse_where(match.group(3))
    if "ID" in set_clause:
        raise ValueError("столбец ID нельзя изменить.")
    if not (check_clause(metadata, table_name, set_clause)
            and check_clause(metadata, table_name, where)):
        return

    table_data = load_table_data(table_name)
    found_ids = [row["ID"] for row in find_rows(table_data, where)]
    if not found_ids:
        print("Записи не найдены.")
        return
    table_data = update(table_data, set_clause, where)
    if table_data is None:
        return
    save_table_data(table_name, table_data)
    for row_id in found_ids:
        print(f'Запись с ID={row_id} в таблице "{table_name}" '
              "успешно обновлена.")


@handle_db_errors
def handle_delete(metadata, match):
    table_name, where = match.group(1), parse_where(match.group(2))
    get_columns(metadata, table_name)
    if not check_clause(metadata, table_name, where):
        return

    table_data = load_table_data(table_name)
    found_ids = [row["ID"] for row in find_rows(table_data, where)]
    if not found_ids:
        print("Записи не найдены.")
        return
    table_data = delete(table_data, where)
    if table_data is None:
        return  # операция отменена
    save_table_data(table_name, table_data)
    for row_id in found_ids:
        print(f'Запись с ID={row_id} успешно удалена из таблицы '
              f'"{table_name}".')


def handle_info(metadata, match):
    table_name = match.group(1)
    info(metadata, table_name, load_table_data(table_name))


COMMANDS = {
    "insert": (INSERT_RE, handle_insert),
    "select": (SELECT_RE, handle_select),
    "update": (UPDATE_RE, handle_update),
    "delete": (DELETE_RE, handle_delete),
    "info": (INFO_RE, handle_info),
}


def run():
    """Главный цикл программы."""
    print_help()

    while True:
        metadata = load_metadata()

        try:
            user_input = prompt.string(">>>Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        command = user_input.split()[0].lower()

        match command:
            case "create_table" | "drop_table":
                try:
                    args = shlex.split(user_input)[1:]
                except ValueError:
                    print(f"Некорректное значение: {user_input}. "
                          "Попробуйте снова.")
                    continue
                if command == "create_table":
                    handle_create_table(metadata, args)
                else:
                    handle_drop_table(metadata, args)
            case "list_tables":
                list_tables(metadata)
            case "insert" | "select" | "update" | "delete" | "info":
                regex, handler = COMMANDS[command]
                match_obj = regex.match(user_input)
                if not match_obj:
                    print(f"Некорректное значение: {user_input}. "
                          "Попробуйте снова.")
                    continue
                handler(metadata, match_obj)
            case "help":
                print_help()
            case "exit":
                break
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
