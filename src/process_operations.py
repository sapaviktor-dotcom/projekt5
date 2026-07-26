import re
from collections import Counter
from typing import Any, Dict, List


def process_bank_search(transactions: List[Dict[str, Any]], search_query: str) -> List[Dict[str, Any]]:
    """
    Поиск транзакций по описанию с использованием регулярных выражений.

    Args:
        transactions: Список словарей с данными о транзакциях
        search_query: Строка для поиска в описании

    Returns:
        List[Dict[str, Any]]: Список транзакций, содержащих искомую строку в описании

    Examples:
        >>> transactions = [
        ...     {"description": "Перевод на карту"},
        ...     {"description": "Оплата услуг"}
        ... ]
        >>> process_bank_search(transactions, "карту")
        [{"description": "Перевод на карту"}]
    """
    if not search_query:
        return transactions

    pattern = re.compile(re.escape(search_query), re.IGNORECASE)
    result = []

    for transaction in transactions:
        description = transaction.get("description", "")
        if pattern.search(description):
            result.append(transaction)

    return result


def process_bank_operations(transactions: List[Dict[str, Any]], categories: List[str]) -> Dict[str, int]:
    """
    Подсчет количества транзакций по заданным категориям на основе поля description.

    Args:
        transactions: Список словарей с данными о транзакциях
        categories: Список категорий для подсчета

    Returns:
        Dict[str, int]: Словарь с количеством транзакций по каждой категории

    Examples:
        >>> transactions = [
        ...     {"description": "Перевод на карту"},
        ...     {"description": "Оплата услуг"},
        ...     {"description": "Перевод на карту"}
        ... ]
        >>> process_bank_operations(transactions,["Перевод", "Оплата"])
        {"Перевод": 2, "Оплата": 1}
    """
    category_counter = Counter()

    for transaction in transactions:
        description = transaction.get("description", "")
        for category in categories:
            if category.lower() in description.lower():
                category_counter[category] += 1
                break

    return dict(category_counter)
