import json
import os
from typing import Any, Dict, List


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
    try:
        # Проверяем существование файла
        if not os.path.exists(file_path):
            return []

        # Проверяем, что файл не пустой
        if os.path.getsize(file_path) == 0:
            return []

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Проверяем, что данные являются списком
        if not isinstance(data, list):
            return []

        return data

    except (json.JSONDecodeError, IOError, PermissionError) as e:
        # Логируем ошибку если нужно
        print(f"Ошибка чтения файла {file_path}: {e}")
        return []
