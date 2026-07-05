

import requests
import os
import sys
from dotenv import load_dotenv

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils import load_transactions
from src.external_api import convert_transaction_amount


def main():
    """Основная функция демонстрации."""
    # Загружаем переменные окружения
    load_dotenv()

    # Проверяем наличие API ключа
    if not os.getenv('API_KEY'):
        print("Внимание: API ключ не найден в .env файле")
        print("Конвертация валют будет недоступна")

    # Загружаем транзакции
    file_path = 'data/operations.json'
    transactions = load_transactions(file_path)

    if not transactions:
        print(f"Не удалось загрузить транзакции из {file_path}")
        return

    print(f"Загружено {len(transactions)} транзакций")
    print("\n" + "=" * 60)

    # Конвертируем и выводим каждую транзакцию
    for i, transaction in enumerate(transactions, 1):
        amount_in_rub = convert_transaction_amount(transaction)
        original_amount = transaction.get("amount",0 )
        currency = transaction.get('currency', 'RUB')

        print(f"Транзакция #{i}:")


        print(f"  Описание: {transaction.get('description', 'Нет описания')}")
        print(f"  Сумма: {original_amount} {currency}")
        print(f"  В рублях: {amount_in_rub:.2f} RUB")
        print("-" * 40)

    # Подсчет общей суммы в рублях
    total_rub = sum(
        convert_transaction_amount(t) for t in transactions
    )
    print(f"\nОбщая сумма всех транзакций: {total_rub:.2f} RUB")


if __name__ == "__main__":
    main()