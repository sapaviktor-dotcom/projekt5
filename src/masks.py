def get_mask_account(account_number: str) -> str:
    """Функция  принимает на вход номер счета в виде строки и возвращает маску номера по правилу **XXXX"""

    if not isinstance(account_number, str):
        raise ValueError("Ввод должен быть строкой")

    if not account_number.isdigit() or len(account_number) < 4:
        raise ValueError(" Не корректный ввод")

    # Преобразуем в строку на случай, если пришло число

    account_str = str(account_number)

    if len(account_str) != 20:
        raise ValueError("Номер счёта должен содержать 20 цифр")

    # Берем последние 4 цифры и добавляем две звездочки перед ними

    return f"**{account_str[-4:]}"


def get_mask_card_number(card_number: str) -> str:
    """
    Функция принимает на вход номер карты в виде строки и возвращает маску номера по правилу XXX XX** **** XXXX
    """
    if not isinstance(card_number, str):
        raise ValueError("Ввод должен быть строкой")

    if not card_number.isdigit():
        raise ValueError(" Не корректный ввод")
    # Превращаем в строку, если пришло число
    card_str = str(card_number)

    # Проверяем длину номера карты
    if len(card_str) != 16:
        raise ValueError("Номер карты должен содержать 16 цифр")

    # Формируем маску: первые 6 цифр, звезды и последние 4

    mask = f"{card_str[:4]} {card_str[4:6]}** **** {card_str[-4:]}"

    return mask
