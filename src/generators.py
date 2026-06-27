from typing import Any, Dict, Iterator, List


def filter_by_currency(transactions: List[Dict[str, Any]], currency_code: str) -> Iterator[Dict[str, Any]]:
    """
    Фильтрует транзакции по валюте и возвращает итератор.

    Args:
        transactions: Список словарей с транзакциями
        currency_code: Код валюты для фильтрации (например, "USD")

    Yields:
        Транзакции, где валюта соответствует заданной
    """
    for transaction in transactions:
        try:
            currency = transaction.get("operationAmount", {}).get("currency", {}).get("code")
            amount = transaction.get("operationAmount", {}).get("amount")

            if currency is not None and amount is not None and currency == currency_code:
                yield transaction
        except (AttributeError, TypeError):
            continue


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Iterator[str]:
    """
    Генератор, который возвращает описание каждой транзакции по очереди.

    Args:
        transactions: Список словарей с транзакциями

    Yields:
        Описание транзакции (строка)
    """
    for transaction in transactions:
        # Получаем описание транзакции, если поле существует
        description = transaction.get("description")
        if description is not None:
            yield description


def card_number_generator(start: int, stop: int) -> Iterator[str]:
    """
    Генератор номеров банковских карт в заданном диапазоне.

    Args:
        start: Начальное значение (целое число от 1 до 9999999999999999)
        stop: Конечное значение (целое число от start до 9999999999999999)

    Yields:
        Номер карты в формате "XXXX XXXX XXXX XXXX"

    Raises:
        ValueError: Если start или stop выходят за допустимый диапазон
    """
    # Проверка диапазона
    if start < 1 or stop > 9999999999999999:
        raise ValueError("Номер карты должен быть в диапазоне от 1 до 9999999999999999")
    if start > stop:
        raise ValueError("Начальное значение не может быть больше конечного")

    for number in range(start, stop + 1):
        # Форматируем число в 16-значную строку с ведущими нулями
        formatted_number = f"{number:016d}"
        # Добавляем пробелы каждые 4 цифры
        card_number = " ".join(formatted_number[i : i + 4] for i in range(0, 16, 4))
        yield card_number
