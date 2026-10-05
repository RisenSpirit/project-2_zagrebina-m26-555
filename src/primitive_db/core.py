VALID_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    """Создаёт таблицу."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    if not columns:
        print("Некорректное значение: не указаны столбцы. Попробуйте снова.")
        return metadata

    parsed = [{"name": "ID", "type": "int"}]
    seen = {"ID"}
    for col in columns:
        if col.count(":") != 1:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata
        name, col_type = col.split(":")
        if not name or col_type not in VALID_TYPES:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata
        if name in seen:
            print(f'Некорректное значение: столбец "{name}" указан дважды. '
                  "Попробуйте снова.")
            return metadata
        seen.add(name)
        parsed.append({"name": name, "type": col_type})

    metadata[table_name] = {"columns": parsed}
    cols_str = ", ".join(f'{c["name"]}:{c["type"]}' for c in parsed)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

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