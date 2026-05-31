import pytest

from src.masks import get_mask_account, get_mask_card_number


# Тестирование правильности маскирования номера карты
@pytest.mark.parametrize(
    "card_number, expected",
    [
        ("1234567812345678", "1234 56** **** 5678"),
    ],
)
def test_get_mask_card_number_masking(card_number, expected):
    assert get_mask_card_number(card_number) == expected


# Проверка выброса исключения для номера карты неправильной длины
@pytest.mark.parametrize(
    "card_number",
    [
        "12345",
        "12345678901234567",
        "12312345678901234565677",
    ],
)
def test_get_mask_card_number_invalid_length(card_number):
    with pytest.raises(ValueError, match="Номер карты должен содержать 16 цифр"):
        get_mask_card_number(card_number)


# Проверка, что функция корректно обрабатывает входные строки, где отсутствует номер карты
@pytest.mark.parametrize(
    "card_number",
    [
        None,
    ],
)
def test_get_mask_card_number_invalid_input(card_number):
    with pytest.raises(ValueError):
        get_mask_card_number(card_number)


@pytest.mark.parametrize("num_card", ["abcdefabcdefghijklmno"])
def test_get_mask_card_number_exceptions(num_card):
    with pytest.raises(ValueError, match=" Не корректный ввод"):
        get_mask_card_number(num_card)


@pytest.mark.parametrize(
    "num_account, expected",
    [
        ("11111111111111111111", "**1111"),
        ("22222222222222222222", "**2222"),
        ("00000000000000000000", "**0000"),
    ],
)
def test_get_mask_account_valid(num_account, expected):
    assert get_mask_account(num_account) == expected


@pytest.mark.parametrize(
    "num_account",
    [
        "111111",  # меньше 20 цифр
        "12341234123412345",  # больше 20 цифр
        "abcdefabcdefghijklmno",  # нецифровая строка
        "1234_5678_9012_3456",  # с символами
        " 12345678901234567890",  # с пробелом в начале
        "1234567890123456789",  # 19 цифр
    ],
)
def test_get_mask_account_exceptions(num_account):
    with pytest.raises(ValueError):
        get_mask_account(num_account)
