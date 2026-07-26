import pytest
from src.process_operations import process_bank_search, process_bank_operations



class TestProcessBankSearch:
    """Набор тестов для функции поиска транзакций"""

    def test_search_exact_match(self):
        """Поиск точного совпадения"""
        transactions = [
            {"description": "Перевод на карту", "amount": 1000},
            {"description": "Оплата услуг", "amount": 500},
        ]
        result = process_bank_search(transactions, "карту")
        assert len(result) == 1
        assert result[0]["description"] == "Перевод на карту"

    def test_search_case_insensitive(self):
        """Поиск должен игнорировать регистр"""
        transactions = [{"description": "ПЕРЕВОД НА КАРТУ"}, {"description": "оплата услуг"}]
        result = process_bank_search(transactions, "перевод")
        assert len(result) == 1
        assert result[0]["description"] == "ПЕРЕВОД НА КАРТУ"

    def test_search_partial_match(self):
        """Поиск по части слова"""
        transactions = [{"description": "Перевод на карту"}, {"description": "Переводчик онлайн"}]
        result = process_bank_search(transactions, "перевод")
        assert len(result) == 2

    def test_search_no_matches(self):
        """Поиск отсутствующей строки"""
        transactions = [{"description": "Перевод на карту"}, {"description": "Оплата услуг"}]
        result = process_bank_search(transactions, "покупка")
        assert result == []

    def test_search_empty_query(self):
        """Пустой поисковый запрос должен возвращать все транзакции"""
        transactions = [{"description": "Перевод на карту"}, {"description": "Оплата услуг"}]
        result = process_bank_search(transactions, "")
        assert result == transactions

    def test_search_empty_description(self):
        """Транзакции с пустым описанием не должны находиться"""
        transactions = [{"description": ""}, {"description": "Перевод на карту"}]
        result = process_bank_search(transactions, "перевод")
        assert len(result) == 1
        assert result[0]["description"] == "Перевод на карту"

    def test_search_missing_description_key(self):
        """Транзакции без ключа 'description' должны обрабатываться корректно"""
        transactions = [{"amount": 1000}, {"description": "Перевод на карту", "amount": 500}]  # Нет description
        result = process_bank_search(transactions, "перевод")
        assert len(result) == 1
        assert result[0]["description"] == "Перевод на карту"

    def test_search_unicode_characters(self):
        """Поиск с юникод-символами"""
        transactions = [{"description": "Перевод в €вро"}, {"description": "Оплата в долларах"}]
        result = process_bank_search(transactions, "€")
        assert len(result) == 1
        assert "€" in result[0]["description"]


class TestProcessBankOperations:
    """Набор тестов для функции подсчета транзакций по категориям"""

    def test_count_single_category(self):
        """Подсчет транзакций одной категории"""
        transactions = [
            {"description": "Перевод на карту"},
            {"description": "Оплата услуг"},
            {"description": "Перевод на карту"},
        ]
        result = process_bank_operations(transactions, ["Перевод"])
        assert result == {"Перевод": 2}

    def test_count_multiple_categories(self):
        """Подсчет транзакций по нескольким категориям"""
        transactions = [
            {"description": "Перевод на карту"},
            {"description": "Оплата услуг"},
            {"description": "Перевод на карту"},
            {"description": "Покупка продуктов"},
        ]
        result = process_bank_operations(transactions, ["Перевод", "Оплата", "Покупка"])
        assert result == {"Перевод": 2, "Оплата": 1, "Покупка": 1}

    def test_count_case_insensitive(self):
        """Подсчет должен игнорировать регистр"""
        transactions = [{"description": "ПЕРЕВОД НА КАРТУ"}, {"description": "перевод наличными"}]
        result = process_bank_operations(transactions, ["Перевод"])
        assert result == {"Перевод": 2}

    def test_count_partial_match(self):
        """Подсчет по частичному совпадению"""
        transactions = [{"description": "Перевод на карту"}, {"description": "Переводчик онлайн"}]
        result = process_bank_operations(transactions, ["Перевод"])
        assert result == {"Перевод": 2}

    def test_count_empty_categories(self):
        """Пустой список категорий должен возвращать пустой словарь"""
        transactions = [{"description": "Перевод на карту"}, {"description": "Оплата услуг"}]
        result = process_bank_operations(transactions, [])
        assert result == {}

    def test_count_with_missing_description(self):
        """Транзакции без description не должны учитываться"""
        transactions = [{"amount": 1000}, {"description": "Перевод на карту"}]  # Нет description
        result = process_bank_operations(transactions, ["Перевод"])
        assert result == {"Перевод": 1}

    def test_count_special_characters(self):
        """Подсчет с специальными символами в категориях"""
        transactions = [{"description": "Оплата + услуги"}, {"description": "Оплата услуг"}]
        result = process_bank_operations(transactions, ["Оплата +"])
        assert result == {"Оплата +": 1}

    def test_count_multiple_transactions_same_category(self):
        """Много транзакций одной категории"""
        transactions = [{"description": f"Перевод #{i}"} for i in range(100)]
        result = process_bank_operations(transactions, ["Перевод"])
        assert result == {"Перевод": 100}
