from src.decorators import log


# Пример 1: Логирование в файл
@log(filename="mylog.txt")
def my_function(x: int, y: int) -> int:
    """Простая функция сложения."""
    return x + y


# Пример 2: Логирование в консоль
@log()
def greet(name: str) -> str:
    """Функция приветствия."""
    return f"Hello, {name}!"


# Пример 3: Функция с ошибкой
@log(filename="mylog.txt")
def divide(a: float, b: float) -> float:
    """Функция деления."""
    return a / b


if __name__ == "__main__":
    print("=== Демонстрация работы декоратора log ===\n")

    # Успешное выполнение с записью в файл
    print("1. Вызов my_function(1, 2)")
    result = my_function(1, 2)
    print(f"   Результат: {result}\n")

    # Успешное выполнение с выводом в консоль
    print("2. Вызов greet('Alice')")
    result = greet("Alice")
    print(f"   Результат: {result}\n")

    # Выполнение с ошибкой
    print("3. Вызов divide(10, 0)")
    try:
        result = divide(10, 0)
        print(f"   Результат: {result}")
    except ZeroDivisionError as e:
        print(f"   Перехвачена ошибка: {e}")

    print("\n=== Проверьте содержимое mylog.txt ===")