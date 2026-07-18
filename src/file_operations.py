import csv
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


def read_transactions_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Считывает финансовые операции из CSV файла и возвращает список словарей.

    Args:
        file_path (str): Путь к CSV файлу

    Returns:
        List[Dict[str, Any]]: Список словарей с транзакциями

    Raises:
        FileNotFoundError: Если файл не найден
        pd.errors.EmptyDataError: Если файл пуст
        Exception: При других ошибках чтения файла

    Example:
        >>> transactions = read_transactions_from_csv('data/transactions.csv')
        >>> print(len(transactions))
        10
    """
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return []
        return df.to_dict("records")
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл {file_path} не найден")
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError(f"Файл {file_path} пуст")
    except Exception as e:
        raise Exception(f"Ошибка при чтении CSV файла: {str(e)}")


def read_transactions_from_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    Считывает финансовые операции из Excel файла и возвращает список словарей.

    Args:
        file_path (str): Путь к Excel файлу

    Returns:
        List[Dict[str, Any]]: Список словарей с транзакциями

    Raises:
        FileNotFoundError: Если файл не найден
        pd.errors.EmptyDataError: Если файл пуст
        Exception: При других ошибках чтения файла

    Example:
        >>> transactions = read_transactions_from_excel('data/transactions_excel.xlsx')
        >>> print(len(transactions))
        10
    """
    try:
        df = pd.read_excel(file_path)
        if df.empty:
            return []
        return df.to_dict("records")
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл {file_path} не найден")
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError(f"Файл {file_path} пуст")
    except Exception as e:
        raise Exception(f"Ошибка при чтении Excel файла: {str(e)}")
