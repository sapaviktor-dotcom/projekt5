import json
import re
import math
from datetime import datetime
from typing import List, Dict, Any
from src.processing import filter_by_state, sort_by_date
from src.process_operations import process_bank_operations, process_bank_search
from src.widget import get_date, mask_account_card
from src.file_operations import read_transactions_from_csv, read_transactions_from_excel
from src.utils import load_transactions


# ===== КЛАСС UniversalTransactionParser =====
class UniversalTransactionParser:
    """Универсальный парсер транзакций для разных форматов."""

    @staticmethod
    def safe_str(value):
        """Безопасно преобразует значение в строку, обрабатывая nan и None."""
        if value is None:
            return ""
        if isinstance(value, float) and math.isnan(value):
            return ""
        return str(value).strip()

    @staticmethod
    def parse_date(date_raw):
        """Парсит дату в формат ДД.ММ.ГГГГ."""
        date_str = UniversalTransactionParser.safe_str(date_raw)
        if not date_str:
            return ""

        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%d.%m.%Y')
        except:
            try:
                dt = datetime.fromisoformat(date_str.split('.')[0])
                return dt.strftime('%d.%m.%Y')
            except:
                return date_str.split("T")[0].replace("-", ".")

    @staticmethod
    def mask_account(account):
        """Маскирует номер карты или счета."""
        account_str = UniversalTransactionParser.safe_str(account)
        if not account_str:
            return ""

        if account_str.startswith("Счет"):
            parts = account_str.split()
            if len(parts) == 2:
                return f"Счет **{parts[1][-4:]}"
            return account_str

        parts = account_str.split()
        if len(parts) >= 2:
            card_type = " ".join(parts[:-1])
            card_number = parts[-1]
            if len(card_number) >= 16:
                return f"{card_type} {card_number[:4]} ******** {card_number[-4:]}"

        return account_str

    @classmethod
    def parse(cls, data):
        """
        Универсальный парсер, определяющий формат автоматически.
        """
        # Формат 3: Строка с разделителем
        if isinstance(data, dict) and len(data) == 1:
            key = list(data.keys())[0]
            if ';' in key and any(field in key for field in ['id', 'date', 'amount', 'description']):
                headers = key.split(';')
                values = data[key].split(';')
                transaction = dict(zip(headers, values))

                if 'amount' in transaction:
                    try:
                        transaction['amount'] = float(transaction['amount'])
                    except:
                        pass

                return cls._parse_flat(transaction)

        # Формат 1: Вложенный (с operationAmount)
        if isinstance(data, dict) and "operationAmount" in data:
            return cls._parse_nested(data)

        # Формат 2: Плоский словарь
        if isinstance(data, dict):
            return cls._parse_flat(data)

        # Если строка с разделителем
        if isinstance(data, str) and ';' in data:
            return cls._parse_csv_string(data)

        return None

    @classmethod
    def _parse_nested(cls, transaction):
        """Парсит вложенный формат."""
        op_amount = transaction.get("operationAmount", {})
        currency = op_amount.get("currency", {})

        return {
            'id': cls.safe_str(transaction.get('id', '')),
            'state': cls.safe_str(transaction.get('state', '')),
            'date': cls.parse_date(transaction.get("date", "")),
            'date_raw': cls.safe_str(transaction.get("date", "")),
            'description': cls.safe_str(transaction.get("description", "")),
            'amount': float(op_amount.get("amount", 0)),
            'currency_code': currency.get("code", "RUB"),
            'currency_name': cls.safe_str(currency.get("name", "")),
            'from': cls.safe_str(transaction.get("from", "")),
            'to': cls.safe_str(transaction.get("to", "")),
            'from_masked': cls.mask_account(transaction.get("from", "")),
            'to_masked': cls.mask_account(transaction.get("to", ""))
        }

    @classmethod
    def _parse_flat(cls, transaction):
        """Парсит плоский формат."""
        # Нормализуем все значения в строки
        normalized = {}
        for k, v in transaction.items():
            normalized[k.lower()] = cls.safe_str(v)

        amount = 0
        if 'amount' in normalized:
            try:
                amount = float(normalized['amount'])
            except (ValueError, TypeError):
                amount = 0

        return {
            'id': normalized.get('id', ''),
            'state': normalized.get('state', ''),
            'date': cls.parse_date(normalized.get("date", "")),
            'date_raw': normalized.get("date", ""),
            'description': normalized.get("description", ""),
            'amount': amount,
            'currency_code': normalized.get('currency_code', 'RUB'),
            'currency_name': normalized.get('currency_name', ''),
            'from': normalized.get("from", ""),
            'to': normalized.get("to", ""),
            'from_masked': cls.mask_account(normalized.get("from", "")),
            'to_masked': cls.mask_account(normalized.get("to", ""))
        }

    @classmethod
    def _parse_csv_string(cls, csv_string):
        """Парсит CSV строку."""
        lines = csv_string.strip().split('\n')
        headers = ['id', 'state', 'date', 'amount', 'currency_name',
                   'currency_code', 'from', 'to', 'description']

        transactions = []
        for line in lines:
            if not line.strip():
                continue
            values = line.split(';')
            if len(values) == len(headers):
                transaction = dict(zip(headers, values))
                transactions.append(cls._parse_flat(transaction))

        return transactions if len(transactions) > 1 else (transactions[0] if transactions else None)


# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С ТРАНЗАКЦИЯМИ =====

def get_transactions_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Загрузка транзакций из JSON-файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл {file_path} не найден")
        return []
    except json.JSONDecodeError:
        print(f"Ошибка при чтении JSON-файла {file_path}")
        return []


def filter_by_status(transactions: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    """Фильтрация транзакций по статусу."""
    return [t for t in transactions if t.get("state", "").upper() == status.upper()]


def sort_transactions_by_date(transactions: List[Dict[str, Any]], ascending: bool = False) -> List[Dict[str, Any]]:
    """Сортировка транзакций по дате."""

    def parse_date(transaction):
        date_str = transaction.get('date', '')
        if not date_str:
            return datetime.min

        # Если дата в формате ДД.ММ.ГГГГ
        if '.' in date_str and len(date_str) == 10:
            try:
                return datetime.strptime(date_str, '%d.%m.%Y')
            except:
                pass

        # Пробуем ISO форматы
        for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S.%f',
                    '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        if 'T' in date_str:
            try:
                return datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
            except:
                pass

        return datetime.min

    return sorted(
        transactions,
        key=lambda x: parse_date(x),
        reverse=not ascending
    )


def filter_by_currency(transactions: List[Dict[str, Any]], currency: str = "RUB") -> List[Dict[str, Any]]:
    """Фильтрация транзакций по валюте."""
    return [t for t in transactions if t.get("currency", {}).get("code", "").upper() == currency.upper()]


def format_transaction(transaction: Dict[str, Any]) -> str:
    """Форматирование транзакции для вывода."""
    date = transaction.get("date", "")
    description = transaction.get("description", "")
    amount = transaction.get("amount", 0)
    currency = transaction.get("currency", {}).get("code", "RUB")
    from_account = transaction.get("from_masked", transaction.get("from", ""))
    to_account = transaction.get("to_masked", transaction.get("to", ""))

    result = f"\n{date} {description}\n"
    if from_account and to_account:
        result += f"{from_account} -> {to_account}\n"
    result += f"Сумма: {amount} {currency}"

    return result


def print_transactions(transactions: List[Dict[str, Any]]):
    """Вывод списка транзакций в консоль."""
    if not transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    print(f"\nВсего банковских операций в выборке: {len(transactions)}")
    for transaction in transactions:
        print(format_transaction(transaction))


def get_user_choice(prompt: str, valid_options: List[str]) -> str:
    """Получение выбора пользователя с проверкой корректности."""
    while True:
        choice = input(prompt).strip().upper()
        if choice in [opt.upper() for opt in valid_options]:
            return choice
        print(f"Некорректный ввод. Допустимые варианты: {', '.join(valid_options)}")


def normalize_transaction(transaction_data):
    """
    Нормализует транзакцию из любого формата в единый вид.
    """
    parser = UniversalTransactionParser()

    # Если данные в формате 3 (словарь с одним ключом-заголовком)
    if isinstance(transaction_data, dict) and len(transaction_data) == 1:
        key = list(transaction_data.keys())[0]
        if ';' in key and 'id' in key:
            headers = key.split(';')
            values = transaction_data[key].split(';')
            transaction_data = dict(zip(headers, values))

    parsed = parser.parse(transaction_data)

    if not parsed:
        return None

    return {
        'date': parsed['date'],
        'date_raw': parsed['date_raw'],
        'description': parsed['description'],
        'amount': parsed['amount'],
        'currency': {'code': parsed['currency_code'], 'name': parsed['currency_name']},
        'from': parsed['from'],
        'to': parsed['to'],
        'from_masked': parsed['from_masked'],
        'to_masked': parsed['to_masked'],
        'state': parsed['state'],
        'id': parsed['id']
    }


def main():
    """Основная функция программы."""
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    choice = input("Ваш выбор: ").strip()

    transactions = []

    if choice == "1":
        print("Для обработки выбран JSON-файл.")
        transactions = load_transactions('data/operations.json')
    elif choice == "2":
        print("Для обработки выбран CSV-файл.")
        transactions = read_transactions_from_csv('data/transactions.csv')
    elif choice == "3":
        print("Для обработки выбран XLSX-файл.")
        transactions = read_transactions_from_excel('data/transactions_excel.xlsx')
    else:
        print("Неверный выбор. Программа завершена.")
        return

    if not transactions:
        print("Не удалось загрузить транзакции.")
        return

    # Нормализуем все транзакции
    normalized_transactions = []
    for t in transactions:
        normalized = normalize_transaction(t)
        if normalized:
            normalized_transactions.append(normalized)

    if not normalized_transactions:
        print("Не удалось распарсить транзакции.")
        return

    transactions = normalized_transactions

    # Фильтрация по статусу
    valid_statuses = ["EXECUTED", "CANCELED", "PENDING"]
    while True:
        print("\nВведите статус, по которому необходимо выполнить фильтрацию.")
        print(f"Доступные для фильтровки статусы: {', '.join(valid_statuses)}")
        status = input("Статус: ").strip().upper()
        if status in valid_statuses:
            break
        print(f'Статус операции "{status}" недоступен.')

    filtered_transactions = filter_by_state(transactions, status)
    print(f'Операции отфильтрованы по статусу "{status}"')

    # Сортировка по дате
    sort_choice = get_user_choice("Отсортировать операции по дате? Да/Нет: ", ["Да", "Нет"])
    if sort_choice == "ДА":
        order = get_user_choice("Отсортировать по возрастанию или по убыванию? ", ["по возрастанию", "по убыванию"])
        ascending = order == "ПО ВОЗРАСТАНИЮ"
        filtered_transactions = sort_transactions_by_date(filtered_transactions, ascending)

    # Фильтрация по валюте
    rub_choice = get_user_choice("Выводить только рублевые транзакции? Да/Нет: ", ["Да", "Нет"])
    if rub_choice == "ДА":
        filtered_transactions = filter_by_currency(filtered_transactions, "RUB")

    # Поиск по описанию
    search_choice = get_user_choice("Отфильтровать список транзакций по определенному слову в описании? Да/Нет: ",
                                    ["Да", "Нет"])
    if search_choice == "ДА":
        search_query = input("Введите слово для поиска: ").strip()
        if search_query:
            filtered_transactions = process_bank_search(filtered_transactions, search_query)

    print("\nРаспечатываю итоговый список транзакций...")
    print_transactions(filtered_transactions)


if __name__ == "__main__":
    main()
