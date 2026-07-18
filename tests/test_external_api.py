import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
import requests

from src.external_api import (
    API_KEY,
    BASE_URL,
    clear_exchange_cache,
    convert_transaction_amount,
    get_amount_from_transaction,
    get_currency_from_transaction,
    get_exchange_rate,
    get_exchange_rate_with_cache,
    get_exchange_rate_with_retry,
)


class TestTransactionHelpers(unittest.TestCase):
    """Тесты для вспомогательных функций извлечения данных."""

    def test_get_amount_from_transaction_with_operation_amount(self):
        """Тест извлечения суммы из operationAmount."""
        transaction = {"id": 1, "operationAmount": {"amount": "31957.58", "currency": {"name": "руб.", "code": "RUB"}}}
        result = get_amount_from_transaction(transaction)
        self.assertEqual(result, 31957.58)

    def test_get_amount_from_transaction_with_direct_amount(self):
        """Тест извлечения суммы из прямого поля amount."""
        transaction = {"id": 1, "amount": "100.50", "currency": "USD"}
        result = get_amount_from_transaction(transaction)
        self.assertEqual(result, 100.50)

    def test_get_amount_from_transaction_missing_amount(self):
        """Тест транзакции без суммы."""
        transaction = {"id": 1}
        result = get_amount_from_transaction(transaction)
        self.assertEqual(result, 0.0)

    def test_get_amount_from_transaction_invalid_amount(self):
        """Тест транзакции с некорректной суммой."""
        transaction = {"operationAmount": {"amount": "invalid", "currency": {"code": "USD"}}}
        result = get_amount_from_transaction(transaction)
        self.assertEqual(result, 0.0)

    def test_get_currency_from_transaction_with_operation_amount(self):
        """Тест извлечения валюты из operationAmount."""
        transaction = {"id": 1, "operationAmount": {"amount": "31957.58", "currency": {"name": "руб.", "code": "RUB"}}}
        result = get_currency_from_transaction(transaction)
        self.assertEqual(result, "RUB")

    def test_get_currency_from_transaction_with_direct_currency(self):
        """Тест извлечения валюты из прямого поля currency."""
        transaction = {"id": 1, "amount": "100.50", "currency": "USD"}
        result = get_currency_from_transaction(transaction)
        self.assertEqual(result, "USD")

    def test_get_currency_from_transaction_missing_currency(self):
        """Тест транзакции без валюты."""
        transaction = {"id": 1}
        result = get_currency_from_transaction(transaction)
        self.assertEqual(result, "RUB")

    def test_get_currency_from_transaction_with_currency_dict(self):
        """Тест извлечения валюты из словаря currency."""
        transaction = {"operationAmount": {"amount": "100.50", "currency": {"code": "EUR", "name": "евро"}}}
        result = get_currency_from_transaction(transaction)
        self.assertEqual(result, "EUR")


class TestExchangeRate(unittest.TestCase):
    """Тесты для функции get_exchange_rate."""

    @patch("src.external_api.requests.get")
    def test_get_exchange_rate_success(self, mock_get):
        """Тест успешного получения курса валют."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "result": 75.50,
            "query": {"from": "USD", "to": "RUB", "amount": 1},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        rate = get_exchange_rate("USD", "RUB")

        self.assertEqual(rate, 75.50)
        mock_get.assert_called_once()

        # Проверяем параметры вызова
        call_args = mock_get.call_args
        self.assertEqual(call_args[0][0], BASE_URL)
        self.assertEqual(call_args[1]["params"]["from"], "USD")
        self.assertEqual(call_args[1]["params"]["to"], "RUB")
        self.assertEqual(call_args[1]["params"]["amount"], 1)
        self.assertEqual(call_args[1]["headers"]["apikey"], API_KEY)

    @patch("src.external_api.requests.get")
    def test_get_exchange_rate_different_currencies(self, mock_get):
        """Тест получения курса для разных валют."""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "result": 0.85}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        rate = get_exchange_rate("EUR", "USD")

        self.assertEqual(rate, 0.85)
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]["params"]["from"], "EUR")
        self.assertEqual(call_args[1]["params"]["to"], "USD")

    @patch("src.external_api.requests.get")
    def test_get_exchange_rate_api_error(self, mock_get):
        """Тест ошибки API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": False,
            "error": {"code": 105, "info": "Invalid currency code: XXX"},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            get_exchange_rate("XXX", "RUB")

        self.assertIn("Ошибка API", str(context.exception))

    @patch("src.external_api.requests.get")
    def test_get_exchange_rate_connection_error(self, mock_get):
        """Тест ошибки соединения."""
        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")

        with self.assertRaises(ConnectionError) as context:
            get_exchange_rate("USD", "RUB")

        self.assertIn("Ошибка соединения", str(context.exception))

    @patch("src.external_api.requests.get")
    def test_get_exchange_rate_timeout(self, mock_get):
        """Тест таймаута."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

        with self.assertRaises(ConnectionError) as context:
            get_exchange_rate("USD", "RUB")

        self.assertIn("таймаут", str(context.exception))

    @patch("src.external_api.API_KEY", None)
    def test_get_exchange_rate_no_api_key(self):
        """Тест отсутствия API ключа."""
        with self.assertRaises(ValueError) as context:
            get_exchange_rate("USD", "RUB")

        self.assertIn("API ключ не найден", str(context.exception))

    @patch("src.external_api.requests.get")
    def test_get_exchange_rate_http_error(self, mock_get):
        """Тест HTTP ошибки."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        with self.assertRaises(ConnectionError) as context:
            get_exchange_rate("USD", "RUB")

        self.assertIn("Ошибка соединения", str(context.exception))


class TestExchangeRateWithRetry(unittest.TestCase):
    """Тесты для функции get_exchange_rate_with_retry."""

    @patch("src.external_api.requests.get")
    def test_retry_success_after_429(self, mock_get):
        """Тест успешного получения курса после ошибки 429."""
        # Первый запрос возвращает 429
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "1"}
        mock_response_429.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Client Error")

        # Второй запрос успешен
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"success": True, "result": 75.50}
        mock_response_success.raise_for_status = Mock()

        mock_get.side_effect = [mock_response_429, mock_response_success]

        with patch("time.sleep", return_value=None):  # Не ждем реального времени
            rate = get_exchange_rate_with_retry("USD", "RUB", max_retries=2)
            self.assertEqual(rate, 75.50)
            self.assertEqual(mock_get.call_count, 2)

    @patch("src.external_api.requests.get")
    def test_retry_other_error(self, mock_get):
        """Тест другой ошибки (не 429)."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        with self.assertRaises(ConnectionError):
            get_exchange_rate_with_retry("USD", "RUB", max_retries=2)

        self.assertEqual(mock_get.call_count, 1)  # Не должно быть повторных попыток


class TestCache(unittest.TestCase):
    """Тесты для кэширования курсов валют."""

    def setUp(self):
        """Очищаем кэш перед каждым тестом."""
        clear_exchange_cache()

    @patch("src.external_api.get_exchange_rate_with_retry")
    def test_cache_hit(self, mock_get_rate):
        """Тест попадания в кэш."""
        mock_get_rate.return_value = 75.50

        # Первый вызов - сохраняем в кэш
        rate1 = get_exchange_rate_with_cache("USD", "RUB")
        self.assertEqual(rate1, 75.50)
        self.assertEqual(mock_get_rate.call_count, 1)

        # Второй вызов - берем из кэша
        rate2 = get_exchange_rate_with_cache("USD", "RUB")
        self.assertEqual(rate2, 75.50)
        self.assertEqual(mock_get_rate.call_count, 1)  # Не увеличилось

    @patch("src.external_api.get_exchange_rate_with_retry")
    def test_cache_different_currencies(self, mock_get_rate):
        """Тест кэширования для разных валют."""
        mock_get_rate.side_effect = [75.50, 85.25]

        # Запрашиваем разные валюты
        rate_usd = get_exchange_rate_with_cache("USD", "RUB")
        rate_eur = get_exchange_rate_with_cache("EUR", "RUB")

        self.assertEqual(rate_usd, 75.50)
        self.assertEqual(rate_eur, 85.25)
        self.assertEqual(mock_get_rate.call_count, 2)

        # Повторные запросы должны быть из кэша
        rate_usd_2 = get_exchange_rate_with_cache("USD", "RUB")
        rate_eur_2 = get_exchange_rate_with_cache("EUR", "RUB")

        self.assertEqual(rate_usd_2, 75.50)
        self.assertEqual(rate_eur_2, 85.25)
        self.assertEqual(mock_get_rate.call_count, 2)  # Не увеличилось

    @patch("src.external_api.get_exchange_rate_with_retry")
    def test_cache_expiration(self, mock_get_rate):
        """Тест истечения срока кэша."""
        mock_get_rate.return_value = 75.50

        # Первый вызов
        rate1 = get_exchange_rate_with_cache("USD", "RUB")
        self.assertEqual(rate1, 75.50)
        self.assertEqual(mock_get_rate.call_count, 1)

        # Имитируем истечение кэша (изменяем timestamp)
        from src.external_api import _exchange_rate_cache

        cache_key = "USD_RUB"
        old_rate, old_timestamp = _exchange_rate_cache[cache_key]
        # Устанавливаем timestamp на 10 минут назад
        _exchange_rate_cache[cache_key] = (old_rate, datetime.now() - timedelta(minutes=10))

        # Второй вызов должен обновить кэш
        mock_get_rate.return_value = 76.00
        rate2 = get_exchange_rate_with_cache("USD", "RUB")
        self.assertEqual(rate2, 76.00)
        self.assertEqual(mock_get_rate.call_count, 2)

    def test_clear_cache(self):
        """Тест очистки кэша."""
        from src.external_api import _exchange_rate_cache

        # Добавляем данные в кэш
        _exchange_rate_cache["USD_RUB"] = (75.50, datetime.now())
        self.assertTrue(len(_exchange_rate_cache) > 0)

        # Очищаем кэш
        clear_exchange_cache()
        self.assertEqual(len(_exchange_rate_cache), 0)


class TestConvertTransactionAmount(unittest.TestCase):
    """Тесты для функции convert_transaction_amount."""

    def setUp(self):
        """Очищаем кэш перед каждым тестом."""
        clear_exchange_cache()

    @patch("src.external_api.get_exchange_rate_with_cache")
    def test_convert_transaction_rub_with_operation_amount(self, mock_get_rate):
        """Тест конвертации RUB транзакции с operationAmount."""
        transaction = {
            "id": 441945886,
            "state": "EXECUTED",
            "date": "2019-08-26T10:50:58.294041",
            "operationAmount": {"amount": "31957.58", "currency": {"name": "руб.", "code": "RUB"}},
            "description": "Перевод организации",
            "from": "Maestro 1596837868705199",
            "to": "Счет 64686473678894779589",
        }

        result = convert_transaction_amount(transaction)
        self.assertEqual(result, 31957.58)
        mock_get_rate.assert_not_called()

    @patch("src.external_api.get_exchange_rate_with_cache")
    def test_convert_transaction_usd_with_operation_amount(self, mock_get_rate):
        """Тест конвертации USD транзакции с operationAmount."""
        mock_get_rate.return_value = 75.50

        transaction = {
            "id": 41428829,
            "state": "EXECUTED",
            "date": "2019-07-03T18:35:29.512364",
            "operationAmount": {"amount": "8221.37", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод организации",
            "from": "MasterCard 7158300734726758",
            "to": "Счет 35383033474447895560",
        }

        result = convert_transaction_amount(transaction)
        expected = 8221.37 * 75.50
        self.assertEqual(result, expected)
        mock_get_rate.assert_called_once_with("USD", "RUB")

    @patch("src.external_api.get_exchange_rate_with_cache")
    def test_convert_transaction_eur_with_operation_amount(self, mock_get_rate):
        """Тест конвертации EUR транзакции с operationAmount."""
        mock_get_rate.return_value = 85.25

        transaction = {"operationAmount": {"amount": "500.00", "currency": {"name": "евро", "code": "EUR"}}}

        result = convert_transaction_amount(transaction)
        expected = 500.00 * 85.25
        self.assertEqual(result, expected)
        mock_get_rate.assert_called_once_with("EUR", "RUB")

    @patch("src.external_api.get_exchange_rate_with_cache")
    def test_convert_transaction_missing_amount(self, mock_get_rate):
        """Тест транзакции без суммы."""
        transaction = {"id": 1, "operationAmount": {"currency": {"code": "USD"}}}
        result = convert_transaction_amount(transaction)
        self.assertEqual(result, 0.0)
        mock_get_rate.assert_not_called()

    @patch("src.external_api.get_exchange_rate_with_cache")
    def test_convert_transaction_invalid_amount(self, mock_get_rate):
        """Тест транзакции с некорректной суммой."""
        transaction = {"operationAmount": {"amount": "invalid", "currency": {"code": "USD"}}}
        result = convert_transaction_amount(transaction)
        self.assertEqual(result, 0.0)
        mock_get_rate.assert_not_called()

    @patch("src.external_api.get_exchange_rate_with_cache")
    def test_convert_transaction_conversion_error(self, mock_get_rate):
        """Тест ошибки конвертации."""
        mock_get_rate.side_effect = ValueError("API Error")

        transaction = {"operationAmount": {"amount": "100.00", "currency": {"code": "USD"}}}
        result = convert_transaction_amount(transaction)
        self.assertEqual(result, 0.0)
        mock_get_rate.assert_called_once_with("USD", "RUB")

    @patch("src.external_api.get_exchange_rate_with_cache")
    def test_convert_transaction_unsupported_currency(self, mock_get_rate):
        """Тест неподдерживаемой валюты."""
        transaction = {"operationAmount": {"amount": "100.00", "currency": {"code": "GBP"}}}
        result = convert_transaction_amount(transaction)
        self.assertEqual(result, 0.0)
        mock_get_rate.assert_not_called()

    def test_convert_transaction_with_direct_fields(self):
        """Тест конвертации транзакции с прямыми полями (обратная совместимость)."""
        transaction = {"id": 1, "amount": "100.50", "currency": "USD"}
        with patch("src.external_api.get_exchange_rate_with_cache") as mock_rate:
            mock_rate.return_value = 75.50
            result = convert_transaction_amount(transaction)
            self.assertEqual(result, 100.50 * 75.50)

    @patch("src.external_api.get_exchange_rate_with_cache")
    def test_convert_multiple_transactions(self, mock_get_rate):
        """Тест конвертации нескольких транзакций."""
        mock_get_rate.return_value = 75.50

        transactions = [
            {"operationAmount": {"amount": "100.00", "currency": {"code": "USD"}}},
            {"operationAmount": {"amount": "200.00", "currency": {"code": "EUR"}}},
            {"operationAmount": {"amount": "1000.00", "currency": {"code": "RUB"}}},
        ]

        results = [convert_transaction_amount(t) for t in transactions]

        self.assertEqual(results[0], 100.00 * 75.50)
        self.assertEqual(results[1], 200.00 * 75.50)
        self.assertEqual(results[2], 1000.00)
        self.assertEqual(mock_get_rate.call_count, 2)

    def test_convert_transaction_zero_amount(self):
        """Тест с нулевой суммой."""
        transaction = {"operationAmount": {"amount": "0.00", "currency": {"code": "USD"}}}
        result = convert_transaction_amount(transaction)
        self.assertEqual(result, 0.0)


# Pytest стиль тесты
@pytest.mark.parametrize(
    "transaction,expected",
    [
        ({"operationAmount": {"amount": "100.00", "currency": {"code": "RUB"}}}, 100.0),
        ({"operationAmount": {"amount": "0.00", "currency": {"code": "RUB"}}}, 0.0),
        ({"operationAmount": {"amount": "100.50", "currency": {"code": "RUB"}}}, 100.5),
    ],
)
def test_convert_rub_transactions(transaction, expected):
    """Параметризованные тесты для RUB транзакций."""
    result = convert_transaction_amount(transaction)
    assert result == expected


@pytest.mark.parametrize("currency", ["USD", "EUR"])
@patch("src.external_api.get_exchange_rate_with_cache")
def test_convert_external_currencies(mock_get_rate, currency):
    """Параметризованные тесты для конвертации валют."""
    mock_get_rate.return_value = 75.50
    transaction = {"operationAmount": {"amount": "100.00", "currency": {"code": currency}}}

    result = convert_transaction_amount(transaction)
    expected = 100.00 * 75.50

    assert result == expected
    mock_get_rate.assert_called_once_with(currency, "RUB")


@pytest.mark.parametrize("currency", ["GBP", "CHF", "JPY", "CNY"])
def test_unsupported_currencies(currency):
    """Тест неподдерживаемых валют."""
    transaction = {"operationAmount": {"amount": "100.00", "currency": {"code": currency}}}
    result = convert_transaction_amount(transaction)
    assert result == 0.0


@pytest.mark.parametrize("amount_str", ["invalid", "abc", "1a2b", "---"])
def test_invalid_amount_formats(amount_str):
    """Тест некорректных форматов суммы."""
    transaction = {"operationAmount": {"amount": amount_str, "currency": {"code": "USD"}}}
    result = convert_transaction_amount(transaction)
    assert result == 0.0
