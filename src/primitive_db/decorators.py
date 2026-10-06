import time

from .constants import CONFIRM_YES, TIME_PRECISION


def handle_db_errors(func):
    """
    Перехватывает типичные ошибки базы данных и выводит понятное сообщение.
    """
    def wrapper(*args, **kwargs):
        """Вызывает функцию внутри блока try/except."""
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. "
                  "Возможно, база данных не инициализирована.")
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
        return None
    return wrapper


def confirm_action(action_name):
    """
    Фабрика декораторов: запрашивает подтверждение опасной операции.
    """
    def decorator(func):
        """Оборачивает функцию запросом подтверждения."""
        def wrapper(*args, **kwargs):
            """Спрашивает пользователя и вызывает функцию при ответе "y"."""
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer.strip().lower() != CONFIRM_YES:
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    """Замеряет время выполнения функции и выводит его в консоль."""
    def wrapper(*args, **kwargs):
        """Вызывает функцию и печатает время её выполнения."""
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за "
              f"{elapsed:.{TIME_PRECISION}f} секунд.")
        return result
    return wrapper


def create_cacher():
    """Создаёт функцию кэширования, хранящую кэш в замыкании."""
    cache = {}

    def cache_result(key, value_func):
        """Возвращает результат из кэша или вычисляет и сохраняет его."""
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    return cache_result
