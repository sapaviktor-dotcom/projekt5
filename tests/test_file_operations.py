from unittest.mock import Mock, mock_open, patch
import pandas as pd
import pytest

from src.file_operations import read_transactions_from_csv, read_transactions_from_excel


class TestReadTransactionsFromCSV:
    """Тесты для функции read_transactions_from_csv."""

    @patch("pandas.read_csv")
    def test_read_transactions_from_csv_success(self, mock_read_csv):
        """Тест успешного чтения CSV файла."""
        mock_data = pd.DataFrame(
            [{"id": 1, "amount": 100.50, "date": "2023-01-01"}, {"id": 2, "amount": 200.75, "date": "2023-01-02"}]
        )
        mock_read_csv.return_value = mock_data

        result = read_transactions_from_csv("test.csv")

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["amount"] == 100.50
        mock_read_csv.assert_called_once_with("test.csv")

    @patch("pandas.read_csv")
    def test_read_transactions_from_csv_empty_file(self, mock_read_csv):
        """Тест чтения пустого CSV файла."""
        mock_read_csv.return_value = pd.DataFrame()

        result = read_transactions_from_csv("empty.csv")

        assert result == []
        mock_read_csv.assert_called_once_with("empty.csv")

    @patch("pandas.read_csv")
    def test_read_transactions_from_csv_file_not_found(self, mock_read_csv):
        """Тест обработки ошибки при отсутствии файла."""
        mock_read_csv.side_effect = FileNotFoundError()

        with pytest.raises(FileNotFoundError) as exc_info:
            read_transactions_from_csv("not_found.csv")
        assert "не найден" in str(exc_info.value)

    @patch("pandas.read_csv")
    def test_read_transactions_from_csv_empty_data_error(self, mock_read_csv):
        """Тест обработки ошибки пустого файла."""
        mock_read_csv.side_effect = pd.errors.EmptyDataError()

        with pytest.raises(pd.errors.EmptyDataError) as exc_info:
            read_transactions_from_csv("empty.csv")
        assert "пуст" in str(exc_info.value)

    @patch("pandas.read_csv")
    def test_read_transactions_from_csv_general_error(self, mock_read_csv):
        """Тест обработки общей ошибки при чтении."""
        mock_read_csv.side_effect = Exception("Ошибка чтения")

        with pytest.raises(Exception) as exc_info:
            read_transactions_from_csv("bad_file.csv")
        assert "Ошибка при чтении CSV файла" in str(exc_info.value)


class TestReadTransactionsFromExcel:
    """Тесты для функции read_transactions_from_excel."""

    @patch("pandas.read_excel")
    def test_read_transactions_from_excel_success(self, mock_read_excel):
        """Тест успешного чтения Excel файла."""
        mock_data = pd.DataFrame(
            [{"id": 1, "amount": 100.50, "date": "2023-01-01"}, {"id": 2, "amount": 200.75, "date": "2023-01-02"}]
        )
        mock_read_excel.return_value = mock_data

        result = read_transactions_from_excel("test.xlsx")

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["amount"] == 100.50
        mock_read_excel.assert_called_once_with("test.xlsx")

    @patch("pandas.read_excel")
    def test_read_transactions_from_excel_empty_file(self, mock_read_excel):
        """Тест чтения пустого Excel файла."""
        mock_read_excel.return_value = pd.DataFrame()

        result = read_transactions_from_excel("empty.xlsx")

        assert result == []
        mock_read_excel.assert_called_once_with("empty.xlsx")

    @patch("pandas.read_excel")
    def test_read_transactions_from_excel_file_not_found(self, mock_read_excel):
        """Тест обработки ошибки при отсутствии Excel файла."""
        mock_read_excel.side_effect = FileNotFoundError()

        with pytest.raises(FileNotFoundError) as exc_info:
            read_transactions_from_excel("not_found.xlsx")
        assert "не найден" in str(exc_info.value)

    @patch("pandas.read_excel")
    def test_read_transactions_from_excel_empty_data_error(self, mock_read_excel):
        """Тест обработки ошибки пустого Excel файла."""
        mock_read_excel.side_effect = pd.errors.EmptyDataError()

        with pytest.raises(pd.errors.EmptyDataError) as exc_info:
            read_transactions_from_excel("empty.xlsx")
        assert "пуст" in str(exc_info.value)

    @patch("pandas.read_excel")
    def test_read_transactions_from_excel_general_error(self, mock_read_excel):
        """Тест обработки общей ошибки при чтении Excel."""
        mock_read_excel.side_effect = Exception("Ошибка чтения Excel")

        with pytest.raises(Exception) as exc_info:
            read_transactions_from_excel("bad_file.xlsx")
        assert "Ошибка при чтении Excel файла" in str(exc_info.value)
