import json
import os
import tempfile
import unittest
from unittest.mock import patch

import pytest

from src.utils import load_transactions


class TestLoadTransactions(unittest.TestCase):
    """Тесты для функции load_transactions."""

    def setUp(self):
        """Подготовка перед каждым тестом."""
        # Создаем временный файл для тестов
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file_path = os.path.join(self.temp_dir, "test_operations.json")

    def tearDown(self):
        """Очистка после каждого теста."""
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_valid_json_file(self):
        """Тест загрузки корректного JSON файла."""
        test_data = [
            {"id": 1, "amount": 100.50, "currency": "USD", "date": "2024-01-01"},
            {"id": 2, "amount": 200.75, "currency": "EUR", "date": "2024-01-02"},
            {"id": 3, "amount": 300.00, "currency": "RUB", "date": "2024-01-03"},
        ]

        with open(self.temp_file_path, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        result = load_transactions(self.temp_file_path)

        self.assertEqual(result, test_data)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    def test_empty_file(self):
        """Тест пустого файла."""
        with open(self.temp_file_path, "w", encoding="utf-8") as f:
            f.write("")

        result = load_transactions(self.temp_file_path)
        self.assertEqual(result, [])

    def test_file_not_found(self):
        """Тест отсутствующего файла."""
        result = load_transactions("/path/to/nonexistent/file.json")
        self.assertEqual(result, [])

    def test_invalid_json(self):
        """Тест некорректного JSON."""
        with open(self.temp_file_path, "w", encoding="utf-8") as f:
            f.write('{"invalid": "json" without closing brace')

        result = load_transactions(self.temp_file_path)
        self.assertEqual(result, [])

    def test_not_a_list(self):
        """Тест, когда JSON не является списком."""
        with open(self.temp_file_path, "w", encoding="utf-8") as f:
            json.dump({"key": "value", "data": "not a list"}, f)

        result = load_transactions(self.temp_file_path)
        self.assertEqual(result, [])

    def test_empty_list(self):
        """Тест пустого списка."""
        with open(self.temp_file_path, "w", encoding="utf-8") as f:
            json.dump([], f)

        result = load_transactions(self.temp_file_path)
        self.assertEqual(result, [])

    def test_file_with_permission_error(self):
        """Тест ошибки доступа к файлу."""
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            result = load_transactions(self.temp_file_path)
            self.assertEqual(result, [])

    def test_unicode_content(self):
        """Тест файла с Unicode символами."""
        test_data = [{"id": 1, "description": "Покупка в магазине", "amount": 1000.00}]

        with open(self.temp_file_path, "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False)

        result = load_transactions(self.temp_file_path)
        self.assertEqual(result[0]["description"], "Покупка в магазине")

    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_file_access_error_handling(self, mock_getsize, mock_exists):
        """Тест обработки ошибок доступа к файлу."""
        mock_exists.return_value = True
        mock_getsize.side_effect = OSError("Access error")

        result = load_transactions(self.temp_file_path)
        self.assertEqual(result, [])


# Тесты с использованием pytest
@pytest.mark.parametrize(
    "file_content,expected",
    [
        ([{"id": 1, "amount": 100}], [{"id": 1, "amount": 100}]),
        ([], []),
        ({"not": "list"}, []),
    ],
)
def test_load_transactions_parametrized(file_content, expected, tmp_path):
    """Параметризованные тесты для load_transactions."""
    file_path = tmp_path / "test.json"

    if isinstance(file_content, list):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(file_content, f)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(file_content, f)

    result = load_transactions(str(file_path))
    assert result == expected
