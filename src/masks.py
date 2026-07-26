import logging
import os

# Настройка логгера для модуля masks
logger = logging.getLogger("masks")
logger.setLevel(logging.DEBUG)

# Создаем директорию для логов, если её нет
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настройка file_handler с режимом перезаписи 'w'
file_handler = logging.FileHandler(
    "logs/masks.log", mode="w", encoding="utf-8"  # Перезаписывает файл при каждом запуске
)
file_handler.setLevel(logging.DEBUG)

# Настройка форматтера
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)

# Добавляем handler к логгеру
logger.addHandler(file_handler)

# Добавляем также вывод в консоль для разработки (опционально)
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
# console_formatter = logging.Formatter(
#    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
# )
# console_handler.setFormatter(console_formatter)
# logger.addHandler(console_handler)


def get_mask_account(account_number: str) -> str:
    """
    Функция принимает на вход номер счета в виде строки и возвращает маску номера по правилу **XXXX.

    Args:
        account_number: Номер счета (строка из 20 цифр)

    Returns:
        Замаскированный номер счета

    Raises:
        ValueError: Если входные данные некорректны

    Examples:
       # >>> get_mask_account("64686473678894779589")
        '**9589'
       # >>> get_mask_account("35383033474447895560")
        '**5560'
    """
    logger.info(f"Маскировка номера счета (длина ввода: {len(account_number) if account_number else 0})")

    try:
        # Проверяем тип данных
        if not isinstance(account_number, str):
            logger.error(f"Некорректный тип данных: {type(account_number)}")
            raise ValueError("Ввод должен быть строкой")

        # Проверяем, что строка содержит только цифры
        if not account_number.isdigit():
            logger.error(f"Номер счета содержит не цифры: {account_number[:10]}...")
            raise ValueError("Некорректный ввод: номер счета должен содержать только цифры")

        # Проверяем длину
        if len(account_number) < 4:
            logger.error(f"Номер счета слишком короткий: {len(account_number)} символов")
            raise ValueError("Некорректный ввод: номер счета должен содержать минимум 4 цифры")

        # Формируем маску: ** + последние 4 цифры
        masked = f"**{account_number[-4:]}"
        logger.debug(f"Номер счета замаскирован: {masked}")
        logger.info("Маскировка номера счета успешно завершена")
        return masked

    except ValueError as e:
        logger.error(f"Ошибка при маскировке номера счета: {e}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при маскировке номера счета: {e}")
        raise ValueError(f"Ошибка при маскировке счета: {e}")


def get_mask_card_number(card_number: str) -> str:
    """
    Функция принимает на вход номер карты в виде строки и возвращает маску номера по правилу XXXX XX** **** XXXX.

    Args:
        card_number: Номер карты (строка из 16 цифр)

    Returns:
        Замаскированный номер карты

    Raises:
        ValueError: Если входные данные некорректны

    Examples:
       № >>> get_mask_card_number("1596837868705199")
        '1596 83** **** 5199'
        №>>> get_mask_card_number("7158300734726758")
        '7158 30** **** 6758'
    """
    logger.info(f"Маскировка номера карты (длина ввода: {len(card_number) if card_number else 0})")

    try:
        # Проверяем тип данных
        if not isinstance(card_number, str):
            logger.error(f"Некорректный тип данных: {type(card_number)}")
            raise ValueError("Ввод должен быть строкой")

        # Удаляем пробелы для проверки
        card_clean = card_number.replace(" ", "")

        # Проверяем, что строка содержит только цифры
        if not card_clean.isdigit():
            logger.error(f"Номер карты содержит не цифры: {card_clean[:10]}...")
            raise ValueError("Некорректный ввод: номер карты должен содержать только цифры")

        # Проверяем длину номера карты
        if len(card_clean) != 16:
            logger.error(f"Некорректная длина номера карты: {len(card_clean)} (ожидается 16)")
            raise ValueError("Номер карты должен содержать 16 цифр")

        # Формируем маску: XXXX XX** **** XXXX
        masked = f"{card_clean[:4]} {card_clean[4:6]}** **** {card_clean[-4:]}"

        logger.debug(f"Номер карты замаскирован: {masked}")
        logger.info("Маскировка номера карты успешно завершена")
        return masked

    except ValueError as e:
        logger.error(f"Ошибка при маскировке номера карты: {e}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при маскировке номера карты: {e}")
        raise ValueError(f"Ошибка при маскировке карты: {e}")
