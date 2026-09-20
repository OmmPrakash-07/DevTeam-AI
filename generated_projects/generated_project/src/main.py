import sys
from .history import add_entry, get_history


def compute(a, b, op):
    """Perform basic arithmetic operation."""
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a / b
    else:
        raise ValueError(f"Unsupported operation: {op}")


def parse_number(input_str):
    try:
        return float(input_str)
    except ValueError:
        raise ValueError(f"Invalid number: {input_str}")


def main():
    print("Simple Python Calculator")
    while True:
        try:
            first = input("Enter first number: ")
            a = parse_number(first)
            op = input("Select operation (+, -, *, /): ").strip()
            second = input("Enter second number: ")
            b = parse_number(second)
            result = compute(a, b, op)
            print(f"Result: {result}")
            add_entry(f"{a} {op} {b}", result)
            cont = input("Perform another calculation? (y/n): ").strip().lower()
            if cont != 'y':
                print("History:")
                for expr, res in get_history():
                    print(f"{expr} = {res}")
                print("Goodbye!")
                break
        except ZeroDivisionError as zde:
            print(f"Error: {zde}")
        except ValueError as ve:
            print(f"Error: {ve}")


if __name__ == "__main__":
    main()
