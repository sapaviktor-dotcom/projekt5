import functools
import os
import sys
import tempfile
import unittest
from datetime import datetime
from io import StringIO
from typing import Any, Callable, Optional
from unittest.mock import mock_open, patch

import pytest

from src.decorators import _format_args, _write_log, log


class TestLogDecorator(unittest.TestCase):
    """Тесты для декоратора log."""

    def setUp(self):
        """Подготовка перед каждым тестом."""
        # Создаем временный файл для тестов
        self.test_filename = "test_log.txt"
        # Очищаем файл перед тестом
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def tearDown(self):
        """Очистка после каждого теста."""
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_log_to_file_success(self):
        """Тест успешного логирования в файл."""

        @log(filename=self.test_filename)
        def add(a, b):
            return a + b

        result = add(2, 3)
        self.assertEqual(result, 5)

        # Проверяем содержимое файла
        with open(self.test_filename, "r", encoding="utf-8") as f:
            content = f.read()

        # Проверяем, что лог содержит имя функции и "ok"
        self.assertIn("add ok", content)

    def test_log_to_console(self):
        """Тест логирования в консоль."""
        # Перенаправляем stdout для перехвата вывода
        captured_output = StringIO()
        sys.stdout = captured_output

        @log()
        def multiply(a, b):
            return a * b

        result = multiply(2, 4)
        self.assertEqual(result, 8)

        # Восстанавливаем stdout
        sys.stdout = sys.__stdout__

        # Проверяем вывод
        output = captured_output.getvalue()
        self.assertIn("multiply ok", output)

    def test_log_error(self):
        """Тест логирования ошибки."""

        @log(filename=self.test_filename)
        def divide(a, b):
            return a / b

        # Вызываем функцию с ошибкой
        with self.assertRaises(ZeroDivisionError):
            divide(10, 0)

        # Проверяем содержимое файла
        with open(self.test_filename, "r", encoding="utf-8") as f:
            content = f.read()

        # Проверяем, что ошибка залогирована
        self.assertIn("divide error", content)
        self.assertIn("ZeroDivisionError", content)
        self.assertIn("Inputs: (10, 0)", content)

    def test_multiple_calls(self):
        """Тест множественных вызовов."""

        @log(filename=self.test_filename)
        def square(x):
            return x**2

        square(2)
        square(3)
        square(4)

        with open(self.test_filename, "r", encoding="utf-8") as f:
            content = f.read()

        # Проверяем, что каждый вызов залогирован
        self.assertEqual(content.count("square ok"), 3)

    def test_kwargs_logging(self):
        """Тест логирования именованных аргументов."""

        @log(filename=self.test_filename)
        def user_info(name, age=None, city=None):
            return f"{name}, {age}, {city}"

        user_info("Alice", age=30, city="New York")

        with open(self.test_filename, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("user_info ok", content)


def test_write_log_to_file():
    """Тест: _write_log запись в файл."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        filename = tmp.name

    try:
        # Запись в файл
        _write_log("Test message\n", filename)

        # Проверка содержимого
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        assert content == "Test message\n"

        # Дополнительная запись
        _write_log("Second message\n", filename)
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        assert content == "Test message\nSecond message\n"

    finally:
        if os.path.exists(filename):
            os.remove(filename)


def test_log_handles_exception_with_custom_message(capsys):
    """Тест: логирование исключения с кастомным сообщением."""

    @log()
    def custom_error_func():
        raise RuntimeError("Custom runtime error message")

    with pytest.raises(RuntimeError) as exc_info:
        custom_error_func()

    assert "Custom runtime error message" in str(exc_info.value)

    captured = capsys.readouterr()
    assert "custom_error_func error: RuntimeError" in captured.out
    assert "Custom runtime error message" not in captured.out  # Сообщение не логируется


def test_log_handles_attribute_error(capsys):
    """Тест: логирование AttributeError."""

    @log()
    def attr_error_func():
        obj = None
        return obj.some_attribute

    with pytest.raises(AttributeError):
        attr_error_func()

    captured = capsys.readouterr()
    assert "attr_error_func error: AttributeError" in captured.out


def test_log_handles_type_error(capsys):
    """Тест: логирование TypeError."""

    @log()
    def type_error_func(a, b):
        return a + b

    with pytest.raises(TypeError):
        type_error_func(1, "2")

    captured = capsys.readouterr()
    assert "type_error_func error: TypeError" in captured.out
    assert "Inputs: (1, '2')" in captured.out


def _format_args(args: tuple, kwargs: dict) -> str:
    """Форматирует аргументы для логирования."""
    parts = []
    if args:
        parts.extend(str(arg) for arg in args)
    if kwargs:
        parts.extend(f"{k}={v}" for k, v in kwargs.items())
    return ", ".join(parts) if parts else "()"


def _write_log(message: str, filename: Optional[str] = None) -> None:
    """Записывает сообщение в файл или в stderr."""
    if filename:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(message)
    else:
        import sys

        sys.stderr.write(message)


if __name__ == "__main__":
    unittest.main()
