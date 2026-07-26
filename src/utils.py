import json
import logging
import os
from typing import Any, Dict, List

# Настройка логгера для модуля utils
logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)

# Создаем директорию для логов, если её нет
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настройка file_handler с режимом перезаписи 'w'
file_handler = logging.FileHandler(
    "logs/utils.log", mode="w", encoding="utf-8"  # Перезаписывает файл при каждом запуске
)
file_handler.setLevel(logging.DEBUG)

# Настройка форматтера
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)

# Добавляем handler к логгеру
logger.addHandler(file_handler)

# Добавляем также вывод в консоль для разработки (опционально)
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
# console_formatter = logging.Formatter(
#    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
# )
# console_handler.setFormatter(console_formatter)
# logger.addHandler(console_handler)


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает транзакции из JSON-файла.

    Args:
        file_path: Путь к JSON-файлу

    Returns:
        Список словарей с данными о транзакциях

    Examples:
        #>>> transactions = load_transactions('data/operations.json')
        #>>> isinstance(transactions, list)
        True
    """
    logger.info(f"Попытка загрузки транзакций из файла: {file_path}")

    try:
        # Проверяем существование файла
        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {file_path}")
            return []

        # Проверяем, что файл не пустой
        if os.path.getsize(file_path) == 0:
            logger.warning(f"Файл пуст: {file_path}")
            return []

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Проверяем, что данные являются списком
        if not isinstance(data, list):
            logger.error(f"Данные в файле не являются списком: {file_path}")
            return []

        logger.info(f"Успешно загружено {len(data)} транзакций из {file_path}")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON в файле {file_path}: {e}")
        return []
    except PermissionError as e:
        logger.error(f"Ошибка доступа к файлу {file_path}: {e}")
        return []
    except IOError as e:
        logger.error(f"Ошибка ввода-вывода при чтении файла {file_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Неожиданная ошибка при чтении файла {file_path}: {e}")
        return []
