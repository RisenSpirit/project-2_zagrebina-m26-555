import shlex

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata


def print_help():
    """Выводит справку по командам."""
    print("\n***База данных***")
    print("\nФункции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. "
          "- создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Главный цикл программы."""
    print_help()

    while True:
        metadata = load_metadata()

        try:
            user_input = input(">>>Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        command, params = args[0], args[1:]

        match command:
            case "create_table":
                if not params:
                    print("Некорректное значение: не указано имя таблицы. "
                          "Попробуйте снова.")
                    continue
                metadata = create_table(metadata, params[0], params[1:])
                save_metadata(metadata)
            case "drop_table":
                if len(params) != 1:
                    print("Некорректное значение: укажите одно имя таблицы. "
                          "Попробуйте снова.")
                    continue
                metadata = drop_table(metadata, params[0])
                save_metadata(metadata)
            case "list_tables":
                list_tables(metadata)
            case "help":
                print_help()
            case "exit":
                break
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
