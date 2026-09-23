from pathlib import Path
import ast
import re
import subprocess
import sys

from graph.state import ProjectState
from tools.filesystem import get_project_dir


def normalize_path(file_path: str) -> str:
    """
    Normalize generated file paths.

    Removes the generated_project/ prefix if present.
    """
    file_path = str(file_path).replace("\\", "/")

    if file_path.startswith("generated_project/"):
        file_path = file_path[len("generated_project/"):]

    return file_path.strip("/")


def is_test_file(file_path: str) -> bool:
    """
    Check whether a file is a test file.
    """
    path = Path(file_path)

    return (
        path.name.startswith("test_")
        or path.name.endswith("_test.py")
    )


def validate_python_file(path: Path) -> dict:
    """
    Validate Python syntax using AST.
    """
    try:
        source = path.read_text(encoding="utf-8")

        ast.parse(source)

        return {
            "status": "passed",
            "file": str(path),
        }

    except SyntaxError as error:
        return {
            "status": "failed",
            "file": str(path),
            "error": (
                f"SyntaxError: {error.msg} "
                f"at line {error.lineno}"
            ),
        }

    except Exception as error:
        return {
            "status": "failed",
            "file": str(path),
            "error": str(error),
        }


def find_external_imports(path: Path) -> list[str]:
    """
    Find imported top-level modules.
    """
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        imports = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):

                for alias in node.names:
                    imports.append(
                        alias.name.split(".")[0]
                    )

            elif isinstance(node, ast.ImportFrom):

                if node.module:
                    imports.append(
                        node.module.split(".")[0]
                    )

        return sorted(set(imports))

    except Exception:
        return []


def parse_unittest_result(output: str) -> dict:
    """
    Parse unittest output.

    Returns:
        {
            "tests_run": int,
            "failures": int,
            "errors": int
        }
    """
    tests_run = 0
    failures = 0
    errors = 0

    # Example:
    # Ran 8 tests in 0.123s
    match = re.search(
        r"Ran\s+(\d+)\s+tests?",
        output,
        re.IGNORECASE,
    )

    if match:
        tests_run = int(match.group(1))

    # Example:
    # FAILED (failures=1)
    match = re.search(
        r"failures=(\d+)",
        output,
        re.IGNORECASE,
    )

    if match:
        failures = int(match.group(1))

    # Example:
    # FAILED (errors=1)
    match = re.search(
        r"errors=(\d+)",
        output,
        re.IGNORECASE,
    )

    if match:
        errors = int(match.group(1))

    return {
        "tests_run": tests_run,
        "failures": failures,
        "errors": errors,
    }


def run_test_suite(project_dir: Path) -> dict:
    """
    Run unittest test discovery inside the generated project.

    Zero discovered tests are considered a tester error because
    the generated test suite did not actually execute.
    """

    tests_dir = project_dir / "tests"

    if not tests_dir.exists():

        return {
            "status": "failed",
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "errors": 1,
            "output": "",
            "error": "No tests directory found.",
        }

    try:

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-v",
            ],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        output = (
            stdout
            + ("\n" if stdout and stderr else "")
            + stderr
        ).strip()

        parsed = parse_unittest_result(output)

        tests_run = parsed["tests_run"]
        failures = parsed["failures"]
        errors_count = parsed["errors"]

        # ---------------------------------------------------------
        # No tests discovered
        # ---------------------------------------------------------

        if tests_run == 0:

            return {
                "status": "failed",
                "tests_run": 0,
                "passed": 0,
                "failed": 0,
                "errors": 1,
                "output": output,
                "error": (
                    "No tests were discovered. "
                    "The generated test suite did not execute."
                ),
            }

        # ---------------------------------------------------------
        # Calculate actual passed test cases
        # ---------------------------------------------------------

        passed = max(
            0,
            tests_run - failures - errors_count,
        )

        # ---------------------------------------------------------
        # All tests passed
        # ---------------------------------------------------------

        if (
            result.returncode == 0
            and failures == 0
            and errors_count == 0
        ):

            return {
                "status": "passed",
                "tests_run": tests_run,
                "passed": passed,
                "failed": 0,
                "errors": 0,
                "output": output,
            }

        # ---------------------------------------------------------
        # Tests executed but one or more failed
        # ---------------------------------------------------------

        return {
            "status": "failed",
            "tests_run": tests_run,
            "passed": passed,
            "failed": failures,
            "errors": errors_count,
            "output": output,
            "error": (
                "One or more unittest test cases failed."
                if failures > 0
                else "One or more unittest test cases produced errors."
            ),
        }

    except subprocess.TimeoutExpired as error:

        return {
            "status": "failed",
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "errors": 1,
            "output": "",
            "error": "Test suite timed out after 30 seconds.",
        }

    except Exception as error:

        return {
            "status": "failed",
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "errors": 1,
            "output": "",
            "error": str(error),
        }


def run_python_file(
    path: Path,
    project_dir: Path,
) -> dict:
    """
    Run a non-interactive Python file.
    """

    try:

        result = subprocess.run(
            [
                sys.executable,
                str(path),
            ],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:

            return {
                "status": "passed",
                "file": str(path),
                "output": result.stdout.strip(),
            }

        return {
            "status": "failed",
            "file": str(path),
            "error": (
                result.stderr.strip()
                or result.stdout.strip()
                or "Python file execution failed."
            ),
        }

    except subprocess.TimeoutExpired:

        return {
            "status": "skipped",
            "file": str(path),
            "error": (
                "Execution timed out. "
                "File may be interactive."
            ),
        }

    except Exception as error:

        return {
            "status": "failed",
            "file": str(path),
            "error": str(error),
        }


def collect_project_files(
    generated_files: list,
    tasks: list,
) -> list[str]:
    """
    Collect, normalize and deduplicate generated files.
    """

    all_files = []

    for file_path in generated_files:

        if file_path:
            all_files.append(
                str(file_path)
            )

    for task in tasks:

        if not isinstance(task, dict):
            continue

        file_path = task.get("path")

        if file_path:
            all_files.append(
                str(file_path)
            )

    unique_files = []
    seen = set()

    for file_path in all_files:

        normalized = normalize_path(
            file_path
        )

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)
        unique_files.append(normalized)

    return unique_files


def is_interactive_python_file(
    path: Path,
) -> bool:
    """
    Detect Python programs that require user interaction.
    """

    try:

        source = path.read_text(
            encoding="utf-8"
        )

        interactive_markers = [
            "input(",
            "getpass(",
        ]

        return any(
            marker in source
            for marker in interactive_markers
        )

    except Exception:
        return False


def tester_agent(state: ProjectState):

    project_id = state.get("project_id")

    if not project_id:

        error = (
            "Project ID is missing from project state."
        )

        return {
            **state,
            "test_results": {
                "status": "failed",
                "total_files": 0,
                "passed": 0,
                "failed": 1,
                "errors": [error],
                "execution_results": [],
                "test_suite": {
                    "status": "failed",
                    "tests_run": 0,
                    "passed": 0,
                    "failed": 0,
                    "errors": 1,
                    "error": error,
                },
            },
            "errors": [error],
        }

    # -------------------------------------------------------------
    # Project directory
    # -------------------------------------------------------------

    project_dir = get_project_dir(
        project_id
    )

    generated_files = state.get(
        "generated_files",
        [],
    )

    tasks = state.get(
        "tasks",
        [],
    )

    # -------------------------------------------------------------
    # Collect files
    # -------------------------------------------------------------

    unique_files = collect_project_files(
        generated_files,
        tasks,
    )

    syntax_results = []
    execution_results = []
    errors = []

    python_files = []

    # -------------------------------------------------------------
    # Validate Python files
    # -------------------------------------------------------------

    for file_path in unique_files:

        path = project_dir / file_path

        if not path.exists():

            errors.append(
                f"File not found: {file_path}"
            )

            continue

        if path.suffix.lower() != ".py":
            continue

        python_files.append(
            file_path
        )

        syntax_result = validate_python_file(
            path
        )

        syntax_results.append(
            syntax_result
        )

        if syntax_result["status"] == "failed":

            errors.append(
                f"{file_path}: "
                f"{syntax_result.get('error', 'Syntax error')}"
            )

    # -------------------------------------------------------------
    # Detect pytest imports
    # -------------------------------------------------------------

    pytest_detected = []

    for file_path in python_files:

        path = project_dir / file_path

        imports = find_external_imports(
            path
        )

        if "pytest" in imports:

            pytest_detected.append(
                file_path
            )

            errors.append(
                f"{file_path}: pytest import detected. "
                f"Use unittest unless pytest is explicitly required."
            )

    # -------------------------------------------------------------
    # Run unittest suite
    # -------------------------------------------------------------

    test_suite_result = run_test_suite(
        project_dir
    )

    # Do NOT duplicate the complete unittest error
    # into the top-level errors list if it is already
    # represented by failed/error counters.
    if test_suite_result["status"] != "passed":

        test_suite_error = test_suite_result.get(
            "error"
        )

        if test_suite_error:
            errors.append(
                f"Test suite: {test_suite_error}"
            )

    # -------------------------------------------------------------
    # Run non-test Python files
    # -------------------------------------------------------------

    for file_path in python_files:

        if is_test_file(file_path):
            continue

        path = project_dir / file_path

        # Skip interactive programs.
        if is_interactive_python_file(path):

            execution_results.append({
                "status": "skipped",
                "file": file_path,
                "reason": (
                    "Interactive CLI program."
                ),
            })

            continue

        result = run_python_file(
            path,
            project_dir,
        )

        result["file"] = file_path

        execution_results.append(
            result
        )

        if result["status"] == "failed":

            errors.append(
                f"{file_path}: "
                f"{result.get('error', 'Execution failed')}"
            )

    # -------------------------------------------------------------
    # Syntax failures
    # -------------------------------------------------------------

    syntax_failed = sum(
        1
        for result in syntax_results
        if result["status"] == "failed"
    )

    # -------------------------------------------------------------
    # Runtime execution failures
    # -------------------------------------------------------------

    execution_failed = sum(
        1
        for result in execution_results
        if result["status"] == "failed"
    )

    # -------------------------------------------------------------
    # Test-case statistics
    # -------------------------------------------------------------

    test_cases_run = test_suite_result.get(
        "tests_run",
        0,
    )

    test_cases_passed = test_suite_result.get(
        "passed",
        0,
    )

    test_cases_failed = test_suite_result.get(
        "failed",
        0,
    )

    test_cases_errors = test_suite_result.get(
        "errors",
        0,
    )

    # -------------------------------------------------------------
    # Overall status
    # -------------------------------------------------------------

    overall_status = "passed"

    if errors:
        overall_status = "failed"

    if test_suite_result["status"] != "passed":
        overall_status = "failed"

    if syntax_failed > 0:
        overall_status = "failed"

    if execution_failed > 0:
        overall_status = "failed"

    # -------------------------------------------------------------
    # File statistics
    # -------------------------------------------------------------

    total_files = len(unique_files)

    failed_files = (
        syntax_failed
        + execution_failed
    )

    passed_files = max(
        0,
        total_files - failed_files,
    )

    # -------------------------------------------------------------
    # Final result
    # -------------------------------------------------------------

    return {
        **state,

        "test_results": {

            "status": overall_status,

            "project_id": project_id,

            "project_directory": str(
                project_dir
            ),

            # File-level statistics
            "total_files": total_files,
            "passed": passed_files,
            "failed": failed_files,

            # Test-case statistics
            "tests_run": test_cases_run,
            "tests_passed": test_cases_passed,
            "tests_failed": test_cases_failed,
            "test_errors": test_cases_errors,

            # Detailed tester errors
            "errors": errors,

            # Detailed results
            "syntax_results": syntax_results,
            "execution_results": execution_results,

            # unittest information
            "test_suite": test_suite_result,

            # Dependency check
            "pytest_detected": pytest_detected,
        },

        "errors": errors,
    }