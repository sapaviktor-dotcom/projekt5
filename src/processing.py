from datetime import datetime
from typing import Any, Dict, List


def filter_by_state(transactions: List[Dict[str, Any]], state: str = "EXECUTED") -> List[Dict[str, Any]]:
    """
      Принимает список словарей и опционально значение для ключа 'state'(по умолчанию 'EXECUTED'),
     и возвращает новый список словарей, содержащий только те словари,
    у которых ключ 'state' соответствует указанному значению.
    """

    return [data for data in transactions if data.get("state") == state]


def sort_by_date(transactions: List[Dict[str, Any]], ascending: bool = False) -> List[Dict[str, Any]]:
    """
    Сортировка списка транзакций по дате.
    """

    def get_date(transaction):
        date_str = transaction.get("date", "")
        if not date_str:
            return datetime.min

        # Если дата в формате ДД.ММ.ГГГГ
        if "." in date_str and len(date_str) == 10:
            try:
                return datetime.strptime(date_str, "%d.%m.%Y")
            except:
                pass

        # Пробуем ISO форматы
        for fmt in ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
            try:
                return datetime.strptime(date_str.split("Z")[0], fmt)
            except:
                continue

        return datetime.min

    return sorted(transactions, key=lambda x: get_date(x), reverse=not ascending)
