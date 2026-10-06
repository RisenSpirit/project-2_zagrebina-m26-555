from .constants import (
    ASSIGN_SIGN,
    CLOSE_BRACKET,
    FALSE_VALUE,
    KW_FROM,
    KW_INTO,
    KW_SET,
    KW_VALUES,
    KW_WHERE,
    OPEN_BRACKET,
    QUOTES,
    TRUE_VALUE,
    VALUES_SEPARATOR,
)


def split_outside_quotes(text, sep=VALUES_SEPARATOR):
    """Делит строку по разделителю, игнорируя разделители внутри кавычек."""
    parts, current, quote = [], [], None
    for ch in text:
        if quote:
            current.append(ch)
            if ch == quote:
                quote = None
        elif ch in QUOTES:
            quote = ch
            current.append(ch)
        elif ch == sep:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if quote:
        raise ValueError("незакрытая кавычка.")
    parts.append("".join(current).strip())
    return parts


def parse_value(raw):
    """Превращает текстовое значение в объект Python.

    "Sergei" -> 'Sergei', 28 -> 28, true -> True, false -> False.
    """
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in QUOTES:
        return raw[1:-1]
    if raw.lower() == TRUE_VALUE:
        return True
    if raw.lower() == FALSE_VALUE:
        return False
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"некорректное значение {raw}. "
                         "Строки должны быть в кавычках.") from None


def parse_values(text):
    """Разбирает список значений: '"Sergei", 28, true' -> ['Sergei', 28, True]."""
    parts = split_outside_quotes(text)
    if any(part == "" for part in parts):
        raise ValueError(f"пустое значение в списке ({text}).")
    return [parse_value(part) for part in parts]


def parse_condition(text):
    """Разбирает 'столбец = значение' -> {'столбец': значение}."""
    column, sign, value = text.partition(ASSIGN_SIGN)
    column, value = column.strip(), value.strip()
    if not sign or not column or not value:
        raise ValueError(f"некорректное условие {text}.")
    return {column: parse_value(value)}


def parse_where(text):
    """Разбирает условие where: 'age = 28' -> {'age': 28}."""
    return parse_condition(text)


def parse_set(text):
    """Разбирает условие set.

    'age = 29, name = "Ivan"' -> {'age': 29, 'name': 'Ivan'}
    """
    result = {}
    for part in split_outside_quotes(text):
        result.update(parse_condition(part))
    return result


def command_error(text):
    """Возвращает ошибку некорректного формата команды."""
    return ValueError(f"некорректный формат команды: {text}")


def parse_insert(text):
    """insert into <таблица> values (<v1>, <v2>, ...) -> (таблица, [значения])."""
    head, sep, tail = text.partition(KW_VALUES)
    words, tail = head.split(), tail.strip()
    if (not sep or len(words) != 3 or words[1] != KW_INTO
            or not tail.startswith(OPEN_BRACKET) or not tail.endswith(CLOSE_BRACKET)):
        raise command_error(text)
    return words[2], parse_values(tail[1:-1])


def parse_select(text):
    """select from <таблица> [where <столбец> = <значение>] -> (таблица, where)."""
    head, sep, condition = text.partition(KW_WHERE)
    words = head.split()
    if len(words) != 3 or words[1] != KW_FROM:
        raise command_error(text)
    return words[2], parse_where(condition) if sep else None


def parse_update(text):
    """update <таблица> set <...> where <...> -> (таблица, set, where)."""
    head, sep, rest = text.partition(KW_SET)
    set_part, sep_where, condition = rest.partition(KW_WHERE)
    words = head.split()
    if not sep or not sep_where or len(words) != 2:
        raise command_error(text)
    return words[1], parse_set(set_part), parse_where(condition)


def parse_delete(text):
    """delete from <таблица> where <столбец> = <значение> -> (таблица, where)."""
    head, sep, condition = text.partition(KW_WHERE)
    words = head.split()
    if not sep or len(words) != 3 or words[1] != KW_FROM:
        raise command_error(text)
    return words[2], parse_where(condition)


def parse_info(text):
    """info <таблица> -> таблица."""
    words = text.split()
    if len(words) != 2:
        raise command_error(text)
    return words[1]
