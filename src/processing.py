
from datetime import datetime
from typing import List, Dict, Any


def filter_by_filter_by_state(transactions: List[Dict[str, Any]], state: str = 'EXECUTED') -> List[Dict[str, Any]]:
    """
          Принимает список словарей и опционально значение для ключа 'state'(по умолчанию 'EXECUTED'),
         и возвращает новый список словарей, содержащий только те словари,
        у которых ключ 'state' соответствует указанному значению.
    """

    return [data for data in transactions if data.get('state') == state]


def sort_by_date(list_dictionary: list[Dict[str, Any]], reverse_order: bool = True) -> List[Dict[str, Any]]:
    """
          Принимает список словарей и необязательный параметр, задающий порядок сортировки (по умолчанию — убывание),
        и возвращает новый список, отсортированный по дате (date).
    """
    # Преобразуем строки дат в объекты datetime для сортировки
    for item in list_dictionary:
        item['date'] = datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%S.%f")

    # Сортируем список словарей по ключу 'date'
    sorted_list: List[Dict[str, Any]] = sorted(list_dictionary, key=lambda x: x['date'], reverse=reverse_order)

    # Преобразуем обратно в строковый формат
    for item in sorted_list:
        item['date'] = item['date'].strftime("%Y-%m-%dT%H:%M:%S.%f")

    return sorted_list
