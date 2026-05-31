from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(number: str) -> str:
    """
    Возвращать строку с замаскированным номером. Для карт и счетов используйте разные типы маскировки.
    Visa Platinum 7000792289606361  -> Visa Platinum 7000 79** **** 6361
    Счет 73654108430135874305  -> Счет **4305
    """
    if not number or not isinstance(number, str):
        raise ValueError("Ошибка: пустая строка или неверный тип данных")

    if "счет" in number.lower():
        account_number = get_mask_account(number[-20:])

        return f"Счет {account_number}"

    card_number = get_mask_card_number(number[-16:])

    return f"{number[:-17]} {card_number}"


def get_date(data: str) -> str:
    """
    Функция принимает на вход строку с датой в формате "2024-03-11T02:26:18.671407"
    и возвращает строку с датой в формате "ДД.ММ.ГГГГ"("11.03.2024").
    :rtype: str
    """
    if not data:
        raise ValueError("Ошибка: дата отсутствует или передана пустая строка ")

    data_time = data[:10].split("-")
    if not all(part.isdigit() for part in data_time):
        raise ValueError("Ошибка: дата содержит недопустимые символы")

    return f"{data_time[2]}.{data_time[1]}.{data_time[0]}"
