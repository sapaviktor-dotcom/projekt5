import re
from typing import Any, Dict, List

import pytest

from src.generators import card_number_generator, filter_by_currency, transaction_descriptions

# ==================== ТЕСТЫ ДЛЯ filter_by_currency ====================


class TestFilterByCurrency:
    """Тесты для функции filter_by_currency"""

    @pytest.fixture
    def sample_transactions(self) -> List[Dict[str, Any]]:
        """Фикстура с примерами транзакций"""
        return [
            {
                "id": 1,
                "operationAmount": {"amount": "100.00", "currency": {"name": "USD", "code": "USD"}},
                "description": "USD transaction 1",
            },
            {
                "id": 2,
                "operationAmount": {"amount": "200.00", "currency": {"name": "EUR", "code": "EUR"}},
                "description": "EUR transaction",
            },
            {
                "id": 3,
                "operationAmount": {"amount": "300.00", "currency": {"name": "USD", "code": "USD"}},
                "description": "USD transaction 2",
            },
            {
                "id": 4,
                "operationAmount": {"amount": "400.00", "currency": {"name": "RUB", "code": "RUB"}},
                "description": "RUB transaction",
            },
        ]

    def test_filter_by_currency_usd(self, sample_transactions):
        """Тест: фильтрация USD транзакций"""
        usd_transactions = list(filter_by_currency(sample_transactions, "USD"))

        assert len(usd_transactions) == 2
        assert all(tx["operationAmount"]["currency"]["code"] == "USD" for tx in usd_transactions)
        assert usd_transactions[0]["id"] == 1
        assert usd_transactions[1]["id"] == 3

    def test_filter_by_currency_eur(self, sample_transactions):
        """Тест: фильтрация EUR транзакций"""
        eur_transactions = list(filter_by_currency(sample_transactions, "EUR"))

        assert len(eur_transactions) == 1
        assert eur_transactions[0]["id"] == 2
        assert eur_transactions[0]["operationAmount"]["currency"]["code"] == "EUR"

    def test_filter_by_currency_no_matches(self, sample_transactions):
        """Тест: валюта отсутствует в транзакциях"""
        gbp_transactions = list(filter_by_currency(sample_transactions, "GBP"))

        assert len(gbp_transactions) == 0
        assert isinstance(gbp_transactions, list)

    def test_filter_by_currency_empty_list(self):
        """Тест: пустой список транзакций"""
        empty_transactions = []
        result = list(filter_by_currency(empty_transactions, "USD"))

        assert len(result) == 0
        assert isinstance(result, list)

    def test_filter_by_currency_missing_fields(self):
        """Тест: транзакции с отсутствующими полями"""
        invalid_transactions = [
            {"id": 1, "description": "No operationAmount"},
            {"id": 2, "operationAmount": {"amount": "100"}},  # No currency
            {"id": 3, "operationAmount": {"currency": {"code": "USD"}}},  # No amount
            {"id": 4, "operationAmount": {"currency": {"name": "USD"}}},  # No code
        ]

        result = list(filter_by_currency(invalid_transactions, "USD"))
        assert len(result) == 0


# ==================== ТЕСТЫ ДЛЯ transaction_descriptions ====================


class TestTransactionDescriptions:
    """Тесты для функции transaction_descriptions"""

    @pytest.fixture
    def sample_transactions(self) -> List[Dict[str, Any]]:
        """Фикстура с транзакциями"""
        return [
            {"id": 1, "description": "Перевод организации"},
            {"id": 2, "description": "Перевод со счета на счет"},
            {"id": 3, "description": "Перевод с карты на карту"},
            {"id": 4, "description": "Оплата услуг"},
            {"id": 5, "description": "Пополнение счета"},
        ]

    def test_transaction_descriptions_normal(self, sample_transactions):
        """Тест: нормальная работа с описаниями"""
        descriptions = list(transaction_descriptions(sample_transactions))

        assert len(descriptions) == 5
        assert descriptions[0] == "Перевод организации"
        assert descriptions[1] == "Перевод со счета на счет"
        assert descriptions[2] == "Перевод с карты на карту"
        assert descriptions[3] == "Оплата услуг"
        assert descriptions[4] == "Пополнение счета"

    def test_transaction_descriptions_empty_list(self):
        """Тест: пустой список транзакций"""
        descriptions = list(transaction_descriptions([]))
        assert len(descriptions) == 0

    def test_transaction_descriptions_single_transaction(self):
        """Тест: список с одной транзакцией"""
        transactions = [{"id": 1, "description": "Тестовая операция"}]
        descriptions = list(transaction_descriptions(transactions))

        assert len(descriptions) == 1
        assert descriptions[0] == "Тестовая операция"

    def test_transaction_descriptions_missing_description(self):
        """Тест: транзакции без поля description"""
        transactions = [
            {"id": 1, "description": "Есть описание"},
            {"id": 2},  # Нет описания
            {"id": 3, "description": None},  # None вместо описания
            {"id": 4, "description": ""},  # Пустое описание
        ]

        descriptions = list(transaction_descriptions(transactions))

        # В зависимости от реализации, может быть None или пропуск
        # Проверяем, что количество и типы корректны
        valid_descriptions = [d for d in descriptions if d]
        assert len(valid_descriptions) == 1
        assert valid_descriptions[0] == "Есть описание"

    def test_transaction_descriptions_generator_behavior(self, sample_transactions):
        """Тест: проверка работы генератора"""
        desc_gen = transaction_descriptions(sample_transactions)

        # Проверяем последовательное получение
        assert next(desc_gen) == "Перевод организации"
        assert next(desc_gen) == "Перевод со счета на счет"

        # Проверяем, что можно использовать в цикле
        remaining = list(desc_gen)
        assert len(remaining) == 3

    def test_transaction_descriptions_preserves_order(self):
        """Тест: сохранение порядка транзакций"""
        transactions = [
            {"id": 1, "description": "First"},
            {"id": 2, "description": "Second"},
            {"id": 3, "description": "Third"},
        ]

        descriptions = list(transaction_descriptions(transactions))
        assert descriptions == ["First", "Second", "Third"]

    def test_transaction_descriptions_with_large_data(self):
        """Тест: работа с большим количеством транзакций"""
        large_transactions = [{"id": i, "description": f"Описание {i}"} for i in range(1000)]
        desc_gen = transaction_descriptions(large_transactions)

        # Проверяем первые 10 элементов
        for i in range(10):
            assert next(desc_gen) == f"Описание {i}"

        # Проверяем, что генератор не создает список в памяти
        import sys

        assert sys.getsizeof(desc_gen) < 1000  # Генератор должен быть маленьким


# ==================== ТЕСТЫ ДЛЯ card_number_generator ====================


class TestCardNumberGenerator:
    """Тесты для генератора card_number_generator"""

    def test_card_number_generator_small_range(self):
        """Тест: маленький диапазон номеров"""
        cards = list(card_number_generator(1, 5))

        expected = [
            "0000 0000 0000 0001",
            "0000 0000 0000 0002",
            "0000 0000 0000 0003",
            "0000 0000 0000 0004",
            "0000 0000 0000 0005",
        ]

        assert cards == expected
        assert len(cards) == 5

    def test_card_number_generator_formatting(self):
        """Тест: корректность форматирования номеров"""
        test_cases = [
            (1, "0000 0000 0000 0001"),
            (123, "0000 0000 0000 0123"),
            (12345, "0000 0000 0001 2345"),
            (123456789, "0000 0001 2345 6789"),
            (1234567890123456, "1234 5678 9012 3456"),
            (9999999999999999, "9999 9999 9999 9999"),
        ]

        for number, expected_format in test_cases:
            result = list(card_number_generator(number, number))
            assert result[0] == expected_format

    def test_card_number_generator_range_boundaries(self):
        """Тест: крайние значения диапазона"""
        # Минимальное значение
        min_card = list(card_number_generator(1, 1))
        assert min_card[0] == "0000 0000 0000 0001"

        # Максимальное значение
        max_card = list(card_number_generator(9999999999999999, 9999999999999999))
        assert max_card[0] == "9999 9999 9999 9999"

        # Диапазон от минимума до максимума (проверяем только первый и последний)
        full_range = card_number_generator(1, 9999999999999999)
        assert next(full_range) == "0000 0000 0000 0001"
        # Перемещаемся к концу (очень много итераций, поэтому не делаем)

    def test_card_number_generator_sequence(self):
        """Тест: последовательность номеров"""
        cards = list(card_number_generator(9999999999999995, 9999999999999999))

        expected = [
            "9999 9999 9999 9995",
            "9999 9999 9999 9996",
            "9999 9999 9999 9997",
            "9999 9999 9999 9998",
            "9999 9999 9999 9999",
        ]

        assert cards == expected

    def test_card_number_generator_invalid_range(self):
        """Тест: невалидный диапазон (start > end)"""
        with pytest.raises(ValueError, match="Начальное значение не может быть больше конечного"):
            list(card_number_generator(10, 5))

    def test_card_number_generator_too_small(self):
        """Тест: значение меньше допустимого"""
        with pytest.raises(ValueError, match="Номер карты должен быть в диапазоне от 1 до 9999999999999999"):
            list(card_number_generator(0, 5))

    def test_card_number_generator_too_large(self):
        """Тест: значение больше допустимого"""
        with pytest.raises(ValueError, match="Номер карты должен быть в диапазоне от 1 до 9999999999999999"):
            list(card_number_generator(10000000000000000, 10000000000000005))

    def test_card_number_generator_edge_range(self):
        """Тест: граничные значения диапазона"""
        # start = end
        single = list(card_number_generator(1234567890123456, 1234567890123456))
        assert len(single) == 1
        assert single[0] == "1234 5678 9012 3456"

        # Диапазон из двух элементов
        two_elements = list(card_number_generator(1234567890123456, 1234567890123457))
        assert len(two_elements) == 2
        assert two_elements[0] == "1234 5678 9012 3456"
        assert two_elements[1] == "1234 5678 9012 3457"

    def test_card_number_generator_generator_behavior(self):
        """Тест: проверка ленивости генератора"""
        card_gen = card_number_generator(1, 10)

        # Генератор должен быть итератором
        assert hasattr(card_gen, "__iter__")
        assert hasattr(card_gen, "__next__")

        # Проверяем последовательное получение
        assert next(card_gen) == "0000 0000 0000 0001"
        assert next(card_gen) == "0000 0000 0000 0002"

        # Пропускаем несколько элементов
        for _ in range(3):
            next(card_gen)

        assert next(card_gen) == "0000 0000 0000 0006"

        # Проверяем истощение генератора
        for _ in range(4):
            next(card_gen)

        with pytest.raises(StopIteration):
            next(card_gen)

    def test_card_number_generator_memory_efficiency(self):
        """Тест: эффективность использования памяти"""
        import sys

        # Создаем генератор для большого диапазона
        card_gen = card_number_generator(1, 1000000)

        # Генератор должен занимать мало памяти
        assert sys.getsizeof(card_gen) < 1000

        # Проверяем, что он не создает все числа сразу
        first_few = [next(card_gen) for _ in range(5)]
        assert first_few[0] == "0000 0000 0000 0001"
        assert first_few[4] == "0000 0000 0000 0005"

    def test_card_number_generator_format_pattern(self):
        """Тест: проверка формата вывода (XXXX XXXX XXXX XXXX)"""
        pattern = re.compile(r"^\d{4} \d{4} \d{4} \d{4}$")

        cards = list(card_number_generator(1, 10))

        for card in cards:
            assert pattern.match(card) is not None, f"Некорректный формат: {card}"

    def test_card_number_generator_leading_zeros(self):
        """Тест: проверка ведущих нулей"""
        cards = list(card_number_generator(1, 5))

        for card in cards:
            assert card.startswith("0000 0000 0000 000")

        # Проверяем номера, которые не требуют много ведущих нулей
        larger_card = list(card_number_generator(1000000000000000, 1000000000000000))
        assert larger_card[0] == "1000 0000 0000 0000"

    @pytest.mark.parametrize(
        "start,end,expected_first,expected_last",
        [
            (1, 3, "0000 0000 0000 0001", "0000 0000 0000 0003"),
            (9999999999999997, 9999999999999999, "9999 9999 9999 9997", "9999 9999 9999 9999"),
            (123455678, 123455680, "0000 0001 2345 5678", "0000 0001 2345 5680"),
        ],
    )
    def test_card_number_generator_parametrized(self, start, end, expected_first, expected_last):
        """Тест: параметризованный тест для разных диапазонов"""
        cards = list(card_number_generator(start, end))
        assert cards[-1] == expected_last
        assert cards[0] == expected_first

        assert len(cards) == end - start + 1
