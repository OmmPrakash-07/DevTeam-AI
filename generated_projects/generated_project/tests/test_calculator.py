import unittest
from src.history import add_entry, get_history, _history
from src.main import compute


class TestCalculator(unittest.TestCase):
    def setUp(self):
        _history.clear()

    def test_addition(self):
        self.assertEqual(compute(2, 3, '+'), 5)

    def test_subtraction(self):
        self.assertEqual(compute(5, 2, '-'), 3)

    def test_multiplication(self):
        self.assertEqual(compute(4, 3, '*'), 12)

    def test_division(self):
        self.assertEqual(compute(10, 2, '/'), 5)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            compute(5, 0, '/')

    def test_invalid_operation(self):
        with self.assertRaises(ValueError):
            compute(1, 1, '^')

    def test_history(self):
        add_entry("1 + 1", 2)
        add_entry("2 * 3", 6)
        h = get_history()
        self.assertEqual(len(h), 2)
        self.assertEqual(h[0], ("1 + 1", 2))
        self.assertEqual(h[1], ("2 * 3", 6))


if __name__ == '__main__':
    unittest.main()
