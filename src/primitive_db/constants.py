# Файлы и директории
META_FILE = "db_meta.json"
DATA_DIR = "data"
DATA_FILE_EXTENSION = ".json"
JSON_INDENT = 4

# Типы столбцов
ID_COLUMN = "ID"
ID_TYPE = "int"
VALID_TYPES = ("int", "str", "bool")
TYPE_MAP = {"int": int, "str": str, "bool": bool}
COLUMN_SEPARATOR = ":"

# Значения в командах
QUOTES = ("'", '"')
TRUE_VALUE = "true"
FALSE_VALUE = "false"
VALUES_SEPARATOR = ","
ASSIGN_SIGN = "="

# Ключевые слова команд
KW_INTO = "into"
KW_FROM = "from"
KW_VALUES = " values "
KW_WHERE = " where "
KW_SET = " set "

# Подтверждение действий
CONFIRM_YES = "y"

# Точность вывода времени выполнения (знаков после запятой)
TIME_PRECISION = 3

# Приглашение ко вводу
PROMPT_TEXT = ">>>Введите команду: "
