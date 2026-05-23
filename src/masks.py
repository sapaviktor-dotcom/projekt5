def get_mask_account(account_number: str) -> str:
    """Функция  принимает на вход номер счета в виде строки и возвращает маску номера по правилу **XXXX"""

    # Преобразуем в строку на случай, если пришло число

    account_str = str(account_number)

    # Берем последние 4 цифры и добавляем две звездочки перед ними

    return f"**{account_str[-4:]}"


def get_mask_card_number(card_number: str) -> str:
    """
    Функция принимает на вход номер карты в виде строки и возвращает маску номера по правилу XXX XX** **** XXXX
    """

    # Превращаем в строку, если пришло число
    card_str = str(card_number)

    # Формируем маску: первые 6 цифр, звезды и последние 4

    mask = f"{card_str[:4]} {card_str[4:6]}** **** {card_str[-4:]}"

    return mask
