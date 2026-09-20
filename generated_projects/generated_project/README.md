# Simple Python CLI Calculator

## Project Overview
This project is a lightweight command-line calculator written in Python. It supports basic arithmetic operations (addition, subtraction, multiplication, division), handles invalid input gracefully, and maintains a history of recent calculations for quick reference.

## Features
- Accept integer or decimal numbers from the user.
- Perform four basic arithmetic operations: **+**, **-**, **\***, **/**.
- Prompt the user to select an operation before entering the second operand.
- Display results clearly with a friendly message.
- Graceful handling of division‑by‑zero and other invalid inputs.
- Continuous operation: after each result the user can perform another calculation or exit.
- Optional in‑memory history of the last *n* calculations (default 5).

## Technology Stack
- **Python 3.8+** (standard library only)
- `collections.deque` for efficient history management.
- `unittest` for automated tests.

## Project Structure
```
src/
├── main.py          # Application entry point and user interaction logic
├── history.py       # History storage and utilities
└── __init__.py

tests/
├── test_calculator.py   # Unit tests for calculation logic and history
└── __init__.py

README.md
setup.py (optional)
requirements.txt (empty or minimal)
```

## Installation Instructions
1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/simple-python-calculator.git
   cd simple-python-calculator
   ```
2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```
3. **Install dependencies** (none required beyond the standard library, but you can add `requirements.txt` if needed)
   ```bash
   pip install -r requirements.txt
   ```

## How to Run the Project
You can run the calculator directly via the module interface:

```bash
python -m src.main
```

Alternatively, if you prefer executing the script file:

```bash
python src/main.py
```

Once started, the CLI will guide you through entering numbers, selecting an operation, and optionally reviewing your calculation history.

## API Information
The project is a command‑line tool and does not expose an HTTP API. All logic resides in the `src` package.

### Key Modules
- **src.main** – Handles user input, performs calculations using `compute`, and displays results.
- **src.history** – Maintains a fixed‑size history of calculations using a `deque` for efficient additions and removals.

## Testing Information
Unit tests are located in the `tests/` directory and use Python’s built‑in `unittest` framework.

To run the tests:
```bash
python -m unittest discover tests
```

All tests should pass, confirming that arithmetic operations, error handling, and history management behave as expected.

## Future Improvements
- **Command‑line argument parsing** using `argparse` to allow non‑interactive usage.
- **Extensible operation registry** (e.g., support exponentiation, modulus, trigonometric functions).
- **Persisted history** (write to a JSON or SQLite file). 
- **Logging** to capture user sessions and errors.
- **GUI front‑end** (e.g., Tkinter or web interface).
- **Continuous integration** pipeline to enforce code quality.
- **Type‑checking** with `mypy` and stricter static analysis.
- **Performance benchmarking** for large‑scale calculations.

---

© 2026 Your Name. All rights reserved.