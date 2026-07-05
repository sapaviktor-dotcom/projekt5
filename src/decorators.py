import functools
import sys
from datetime import datetime
from typing import Any, Callable, Optional


def log(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для логирования выполнения функции.

    Логирует начало и конец выполнения функции, результат или ошибку.

    Args:
        filename (Optional[str]): Имя файла для записи логов.
                                  Если None, логи выводятся в консоль.

    Returns:
        Callable: Декорированная функция.

    Examples:
        #>>> @log(filename="mylog.txt")
        #... def add(x, y):
        #...     return x + y
        #>>> add(1, 2)
        3
        # В файл mylog.txt будет записано: add ok

       # >>> @log()
        #... def divide(a, b):
       # ...     return a / b
       # >>> divide(10, 0)
        # В консоль будет выведено: divide error: ZeroDivisionError. Inputs: (10, 0), {}
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Получаем текущее время для логирования
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            func_name = func.__name__

            # Логируем начало выполнения (опционально)
            start_message = f"[{timestamp}] {func_name} started\n"
            _write_log(start_message, filename)

            try:
                # Выполняем функцию
                result = func(*args, **kwargs)

                # Логируем успешное выполнение
                success_message = f"[{timestamp}] {func_name} ok\n"
                _write_log(success_message, filename)

                return result

            except Exception as e:
                # Формируем сообщение об ошибке
                error_type = type(e).__name__
                args_str = _format_args(args, kwargs)

                error_message = f"[{timestamp}] {func_name} error: {error_type}. Inputs: {args_str}\n"
                _write_log(error_message, filename)

                # Пробрасываем исключение дальше
                raise

        return wrapper

    return decorator


def _write_log(message: str, filename: Optional[str] = None) -> None:
    """
    Вспомогательная функция для записи логов.

    Args:
        message (str): Сообщение для логирования.
        filename (Optional[str]): Имя файла. Если None, вывод в консоль.
    """
    if filename:
        # Запись в файл с кодировкой UTF-8
        with open(filename, "a", encoding="utf-8") as f:
            f.write(message)
    else:
        # Вывод в консоль
        sys.stdout.write(message)


def _format_args(args: tuple, kwargs: dict) -> str:
    """
    Форматирует аргументы для вывода в лог.

    Args:
        args (tuple): Позиционные аргументы.
        kwargs (dict): Именованные аргументы.

    Returns:
        str: Отформатированная строка с аргументами.
    """
    parts = []

    if args:
        parts.append(str(args))

    if kwargs:
        parts.append(str(kwargs))

    return ", ".join(parts) if parts else ""
