ENCODING = "utf-8"
READ_MODE = "r"
WRITE_MODE = "w"

COLUMNS_KEY = "columns"
COL_NAME_KEY = "name"
COL_TYPE_KEY = "type"

INT_TYPE = "int"
STR_TYPE = "str"
BOOL_TYPE = "bool"

OPEN_BRACKET = "("
CLOSE_BRACKET = ")"

CMD_CREATE_TABLE = "create_table"
CMD_DROP_TABLE = "drop_table"
CMD_LIST_TABLES = "list_tables"
CMD_INSERT = "insert"
CMD_SELECT = "select"
CMD_UPDATE = "update"
CMD_DELETE = "delete"
CMD_INFO = "info"
CMD_HELP = "help"
CMD_EXIT = "exit"

# Файлы и директории
META_FILE = "db_meta.json"
DATA_DIR = "data"
DATA_FILE_EXTENSION = ".json"
JSON_INDENT = 4

# Типы столбцов
ID_COLUMN = "ID"
ID_TYPE = INT_TYPE
VALID_TYPES = (INT_TYPE, STR_TYPE, BOOL_TYPE)
TYPE_MAP = {INT_TYPE: int, STR_TYPE: str, BOOL_TYPE: bool}
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
