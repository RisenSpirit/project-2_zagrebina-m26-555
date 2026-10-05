def split_outside_quotes(text, sep=","):
    """Делит строку по разделителю, игнорируя разделители внутри кавычек."""
    parts, current, quote = [], [], None
    for ch in text:
        if quote:
            current.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            current.append(ch)
        elif ch == sep:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if quote:
        raise ValueError("незакрытая кавычка")
    parts.append("".join(current).strip())
    return parts


def parse_value(raw):
    """Превращает текстовое значение в объект Python.

    "Sergei" -> 'Sergei', 28 -> 28, true -> True, false -> False.
    """
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        return raw[1:-1]
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    try:
        return int(raw)
    except ValueError:
        raise ValueError(raw) from None


def parse_values(text):
    """Разбирает список значений: '"Sergei", 28, true' -> ['Sergei', 28, True]."""
    parts = split_outside_quotes(text)
    if any(p == "" for p in parts):
        raise ValueError(text)
    return [parse_value(p) for p in parts]


def parse_condition(text):
    """Разбирает 'столбец = значение' -> {'столбец': значение}."""
    if "=" not in text:
        raise ValueError(text)
    column, value = text.split("=", 1)
    column, value = column.strip(), value.strip()
    if not column or not value:
        raise ValueError(text)
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
