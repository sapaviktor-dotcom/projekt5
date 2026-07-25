
from src.file_operations import read_transactions_from_csv, read_transactions_from_excel


if __name__ == "__main__":
    try:
        csv_transactions = read_transactions_from_csv('data/transactions.csv')
        print(f"Загружено {len(csv_transactions)} транзакций из CSV")
        print(csv_transactions[:2])  # Показать первые две
    except Exception as e:
        print(f"Ошибка при чтении CSV: {e}")

    # Чтение Excel файла
    try:
        excel_transactions = read_transactions_from_excel('data/transactions_excel.xlsx')
        print(f"\nЗагружено {len(excel_transactions)} транзакций из Excel")
        print(excel_transactions[:2])  # Показать первые две
    except Exception as e:
        print(f"Ошибка при чтении Excel: {e}")

    # Чтение с указанием конкретного формата
    try:
        csv_data = read_transactions_from_csv('data/transactions.csv')
        print(f"\nЧтение через CSV функцию: {len(csv_data)} транзакций")
    except Exception as e:
        print(f"Ошибка: {e}")

