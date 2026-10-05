import re
import shlex

import prompt
from prettytable import PrettyTable

from .core import (
    check_type,
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
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


def invalid(value):
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def table_exists(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    return True


def check_clause(metadata, table_name, clause):
    """Проверяет, что столбцы из условия существуют и типы значений верны."""
    types = {c["name"]: c["type"] for c in metadata[table_name]["columns"]}
    for col, value in clause.items():
        if col not in types:
            print(f'Ошибка: Столбец "{col}" не существует.')
            return False
        if not check_type(value, types[col]):
            invalid(f"{value!r} для столбца {col}:{types[col]}")
            return False
    return True


def print_rows(metadata, table_name, rows):
    """Выводит записи в виде таблицы PrettyTable."""
    names = [c["name"] for c in metadata[table_name]["columns"]]
    table = PrettyTable()
    table.field_names = names
    for row in rows:
        table.add_row([row.get(n) for n in names])
    print(table)


def handle_insert(metadata, match):
    table_name, values = match.group(1), parse_values(match.group(2))
    table_data = insert(metadata, table_name, values)
    if table_data is not None:
        save_table_data(table_name, table_data)


def handle_select(metadata, match):
    table_name = match.group(1)
    if not table_exists(metadata, table_name):
        return
    where = parse_where(match.group(2)) if match.group(2) else None
    if where and not check_clause(metadata, table_name, where):
        return
    rows = select(load_table_data(table_name), where)
    if not rows:
        print("Записи не найдены.")
        return
    print_rows(metadata, table_name, rows)


def handle_update(metadata, match):
    table_name = match.group(1)
    if not table_exists(metadata, table_name):
        return
    set_clause, where = parse_set(match.group(2)), parse_where(match.group(3))
    if "ID" in set_clause:
        print("Ошибка: Столбец ID нельзя изменить.")
        return
    if not (check_clause(metadata, table_name, set_clause)
            and check_clause(metadata, table_name, where)):
        return

    table_data = load_table_data(table_name)
    found = select(table_data, where)
    if not found:
        print("Записи не найдены.")
        return
    table_data = update(table_data, set_clause, where)
    save_table_data(table_name, table_data)
    for row in found:
        print(f'Запись с ID={row["ID"]} в таблице "{table_name}" '
              "успешно обновлена.")


def handle_delete(metadata, match):
    table_name, where = match.group(1), parse_where(match.group(2))
    if not table_exists(metadata, table_name):
        return
    if not check_clause(metadata, table_name, where):
        return

    table_data = load_table_data(table_name)
    found = select(table_data, where)
    if not found:
        print("Записи не найдены.")
        return
    table_data = delete(table_data, where)
    save_table_data(table_name, table_data)
    for row in found:
        print(f'Запись с ID={row["ID"]} успешно удалена из таблицы '
              f'"{table_name}".')


DATA_COMMANDS = {
    "insert": (INSERT_RE, handle_insert),
    "select": (SELECT_RE, handle_select),
    "update": (UPDATE_RE, handle_update),
    "delete": (DELETE_RE, handle_delete),
}


def handle_table_command(command, user_input, metadata):
    """Обрабатывает create_table и drop_table."""
    try:
        args = shlex.split(user_input)[1:]
    except ValueError:
        invalid(user_input)
        return
    if not args:
        invalid("не указано имя таблицы")
        return

    if command == "create_table":
        is_new = args[0] not in metadata
        metadata = create_table(metadata, args[0], args[1:])
        if is_new and args[0] in metadata:
            save_table_data(args[0], [])
    else:
        if len(args) != 1:
            invalid(user_input)
            return
        if args[0] in metadata:
            delete_table_data(args[0])
        metadata = drop_table(metadata, args[0])
    save_metadata(metadata)


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
                handle_table_command(command, user_input, metadata)
            case "list_tables":
                list_tables(metadata)
            case "insert" | "select" | "update" | "delete":
                regex, handler = DATA_COMMANDS[command]
                match_obj = regex.match(user_input)
                if not match_obj:
                    invalid(user_input)
                    continue
                try:
                    handler(metadata, match_obj)
                except ValueError:
                    invalid(user_input)
            case "info":
                match_obj = INFO_RE.match(user_input)
                if not match_obj:
                    invalid(user_input)
                    continue
                table_name = match_obj.group(1)
                info(metadata, table_name, load_table_data(table_name))
            case "help":
                print_help()
            case "exit":
                break
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
