import os
import time  # <-- ДОБАВЛЯЕМ ИМПОРТ time
from datetime import datetime, timedelta  # <-- ДОБАВЛЯЕМ ДЛЯ КЭШИРОВАНИЯ
from typing import Any, Dict

import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем API ключ из переменных окружения
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.apilayer.com/exchangerates_data/convert"

# Кэш для хранения курсов валют
_exchange_rate_cache = {}
_cache_timeout = 300  # 5 минут


def get_exchange_rate(from_currency: str, to_currency: str = "RUB") -> float:
    """
    Получает текущий курс обмена валют через внешний API.

    Args:
        from_currency: Код исходной валюты (например, "USD")
        to_currency: Код целевой валюты (по умолчанию "RUB")

    Returns:
        Курс обмена как float

    Raises:
        ValueError: Если API ключ не найден или API вернул ошибку
        ConnectionError: Если проблемы с соединением

    Examples:
        >>> rate = get_exchange_rate("USD")
        >>> isinstance(rate, float)
        True
    """
    if not API_KEY:
        raise ValueError("API ключ не найден. " "УстановитеAPI_KEY в .env файле")

    try:
        headers = {"apikey": API_KEY}
        params = {"from": from_currency, "to": to_currency, "amount": 1}

        response = requests.get(BASE_URL, headers=headers, params=params, timeout=10)

        # Обработка ошибки 429 (Too Many Requests)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"⚠️ Превышен лимит запросов. Ожидание {retry_after} секунд...")
            time.sleep(retry_after)
            # Повторяем запрос
            response = requests.get(BASE_URL, headers=headers, params=params, timeout=10)

        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            return float(data.get("result", 0))
        else:
            error_msg = data.get("error", {}).get("info", "Неизвестная ошибка")
            raise ValueError(f"Ошибка API: {error_msg}")

    except requests.Timeout:
        raise ConnectionError("Превышен таймаут соединения с API")
    except requests.RequestException as e:
        raise ConnectionError(f"Ошибка соединения с API: {e}")


def get_exchange_rate_with_retry(from_currency: str, to_currency: str = "RUB", max_retries: int = 3) -> float:
    """
    Получает курс с автоматическими повторными попытками при ошибках.

    Args:
        from_currency: Код исходной валюты
        to_currency: Код целевой валюты (по умолчанию "RUB")
        max_retries: Максимальное количество попыток

    Returns:
        Курс обмена как float

    Raises:
        ConnectionError: Если не удалось получить курс после всех попыток
    """
    retry_count = 0
    base_delay = 2  # начальная задержка в секундах

    while retry_count < max_retries:
        try:
            return get_exchange_rate(from_currency, to_currency)
        except ConnectionError as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                retry_count += 1
                if retry_count >= max_retries:
                    raise

                # Экспоненциальная задержка
                delay = base_delay**retry_count
                print(f"⚠️ Ошибка 429. Повторная попытка через {delay} секунд...")
                time.sleep(delay)
            else:
                raise

    raise ConnectionError(f"Не удалось получить курс после {max_retries} попыток")


def get_exchange_rate_with_cache(from_currency: str, to_currency: str = "RUB") -> float:
    """
    Получает курс с кэшированием на 5 минут.

    Args:
        from_currency: Код исходной валюты
        to_currency: Код целевой валюты (по умолчанию "RUB")

    Returns:
        Курс обмена как float
    """
    cache_key = f"{from_currency}_{to_currency}"

    # Проверяем кэш
    if cache_key in _exchange_rate_cache:
        rate, timestamp = _exchange_rate_cache[cache_key]
        if datetime.now() - timestamp < timedelta(seconds=_cache_timeout):
            return rate

    # Получаем новый курс
    try:
        rate = get_exchange_rate_with_retry(from_currency, to_currency)
    except (ConnectionError, ValueError) as e:
        # Если в кэше есть устаревшие данные, используем их
        if cache_key in _exchange_rate_cache:
            rate, _ = _exchange_rate_cache[cache_key]
            print(f"⚠️ Использую устаревший курс из кэша: {rate}")
            return rate
        raise e

    # Сохраняем в кэш
    _exchange_rate_cache[cache_key] = (rate, datetime.now())

    return rate


def get_amount_from_transaction(transaction: Dict[str, Any]) -> float:
    """
    Извлекает сумму из транзакции с учетом структуры operationAmount.

    Args:
        transaction: Словарь с данными транзакции

    Returns:
        Сумма транзакции как float

    Examples:
        #>>> transaction = {"operationAmount": {"amount": "100.50", "currency": {"code": "USD"}}}
        #>>> get_amount_from_transaction(transaction)
        #100.5
    """
    # Проверяем наличие operationAmount
    operation_amount = transaction.get("operationAmount")

    if operation_amount is None:
        # Пробуем получить amount напрямую (для обратной совместимости)
        amount = transaction.get("amount")
        if amount is not None:
            try:
                return float(amount)
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    # Извлекаем сумму из operationAmount
    amount = operation_amount.get("amount")
    if amount is None:
        return 0.0

    try:
        return float(amount)
    except (ValueError, TypeError):
        return 0.0


def get_currency_from_transaction(transaction: Dict[str, Any]) -> str:
    """
    Извлекает код валюты из транзакции с учетом структуры operationAmount.

    Args:
        transaction: Словарь с данными транзакции

    Returns:
        Код валюты (например, "RUB", "USD", "EUR")

    Examples:
        #>>> transaction = {"operationAmount": {"currency": {"code": "USD"}}}
        #>>> get_currency_from_transaction(transaction)
        #'USD'
    """
    # Проверяем наличие operationAmount
    operation_amount = transaction.get("operationAmount")

    if operation_amount is None:
        # Пробуем получить currency напрямую (для обратной совместимости)
        currency = transaction.get("currency")
        if currency and isinstance(currency, str):
            return currency
        return "RUB"

    # Извлекаем валюту из operationAmount
    currency_info = operation_amount.get("currency")

    if currency_info is None:
        return "RUB"

    # Если currency_info - словарь с полем code
    if isinstance(currency_info, dict):
        return currency_info.get("code", "RUB")

    # Если currency_info - строка (для обратной совместимости)
    if isinstance(currency_info, str):
        return currency_info

    return "RUB"


def convert_transaction_amount(transaction: Dict[str, Any]) -> float:
    """
    Конвертирует сумму транзакции в рубли.

    Args:
        transaction: Словарь с данными транзакции

    Returns:
        Сумма в рублях как float

    Examples:
        #>>> transaction = {"operationAmount": {"amount": "100", "currency": {"code": "USD"}}}
        #>>> amount = convert_transaction_amount(transaction)
        #>>> isinstance(amount, float)
        #True
    """
    # Извлекаем сумму и валюту из транзакции
    amount = get_amount_from_transaction(transaction)
    currency = get_currency_from_transaction(transaction)

    # Если сумма равна 0, возвращаем 0
    if amount == 0:
        return 0.0

    # Если валюта уже RUB, возвращаем сумму
    if currency == "RUB":
        return amount

    # Конвертируем валюту в RUB (поддерживаем USD и EUR)
    if currency in ["USD", "EUR"]:
        try:
            # Используем кэшированную версию с повторными попытками
            rate = get_exchange_rate_with_cache(currency, "RUB")
            return amount * rate
        except (ConnectionError, ValueError) as e:
            print(f"Ошибка конвертации {currency} в RUB: {e}")
            return 0.0
    else:
        # Если валюта не поддерживается, возвращаем 0
        print(f"Валюта {currency} не поддерживается для конвертации")
        return 0.0


# Очистка кэша (опционально)
def clear_exchange_cache():
    """
    Очищает кэш курсов валют.
    """
    global _exchange_rate_cache
    _exchange_rate_cache.clear()
    print("✅ Кэш курсов валют очищен")
