from pathlib import Path
import ast
import subprocess
import sys

from graph.state import ProjectState


BASE_DIR = (
    Path(__file__).resolve().parents[2]
    / "generated_projects"
)


def normalize_path(path: str) -> str:

    path = str(path).replace(
        "\\",
        "/"
    )

    if path.startswith(
        "generated_project/"
    ):
        path = path[
            len("generated_project/"):
        ]

    return path


def is_test_file(path: Path) -> bool:

    name = path.name.lower()

    return (
        name.startswith("test_")
        or name.endswith("_test.py")
        or "tests" in path.parts
    )


def validate_python_file(path: Path) -> dict:

    try:

        source = path.read_text(
            encoding="utf-8"
        )

        ast.parse(source)

        return {
            "valid": True,
            "source": source,
            "error": ""
        }

    except SyntaxError as error:

        return {
            "valid": False,
            "source": "",
            "error": str(error)
        }

    except UnicodeDecodeError as error:

        return {
            "valid": False,
            "source": "",
            "error": f"Encoding error: {error}"
        }


def find_external_imports(
    source: str
) -> list[str]:

    imports = []

    try:

        tree = ast.parse(source)

    except SyntaxError:

        return imports

    for node in ast.walk(tree):

        if isinstance(
            node,
            ast.Import
        ):

            for alias in node.names:

                imports.append(
                    alias.name.split(".")[0]
                )

        elif isinstance(
            node,
            ast.ImportFrom
        ):

            if node.module:

                imports.append(
                    node.module.split(".")[0]
                )

    return imports


def run_test_suite(
    project_dir: Path
) -> dict:

    try:

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests"
            ],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=20
        )

        return {
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }

    except subprocess.TimeoutExpired:

        return {
            "return_code": -1,
            "stdout": "",
            "stderr": (
                "Test suite timed out "
                "after 20 seconds."
            ),
            "passed": False
        }

    except Exception as error:

        return {
            "return_code": -1,
            "stdout": "",
            "stderr": str(error),
            "passed": False
        }


def run_python_file(
    path: Path,
    project_dir: Path
) -> dict:

    try:

        result = subprocess.run(
            [
                sys.executable,
                str(path)
            ],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=10
        )

        return {
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }

    except subprocess.TimeoutExpired:

        return {
            "return_code": -1,
            "stdout": "",
            "stderr": (
                "Execution timed out "
                "after 10 seconds."
            ),
            "passed": False
        }

    except Exception as error:

        return {
            "return_code": -1,
            "stdout": "",
            "stderr": str(error),
            "passed": False
        }


def tester_agent(
    state: ProjectState
) -> ProjectState:

    generated_files = state.get(
        "generated_files",
        []
    )

    if not generated_files:

        error = (
            "No generated files were found."
        )

        return {
            **state,
            "test_results": {
                "status": "failed",
                "total_files": 0,
                "passed": 0,
                "failed": 1,
                "errors": [error],
                "execution_results": []
            },
            "errors": [error]
        }

    # ----------------------------------------------
    # Normalize duplicate paths
    # ----------------------------------------------

    unique_files = []
    seen = set()

    for file_path in generated_files:

        normalized = normalize_path(
            file_path
        )

        if normalized in seen:
            continue

        seen.add(normalized)

        unique_files.append(
            f"generated_project/{normalized}"
        )

    generated_files = unique_files

    project_dir = (
        BASE_DIR / "generated_project"
    )

    passed = 0
    failed = 0

    errors = []
    execution_results = []

    python_files = []
    test_files = []

    # ----------------------------------------------
    # File validation
    # ----------------------------------------------

    for file_path in generated_files:

        path = BASE_DIR / file_path

        if not path.exists():

            failed += 1

            errors.append(
                f"File does not exist: "
                f"{file_path}"
            )

            continue

        if path.stat().st_size == 0:

            if path.name != "__init__.py":

                failed += 1

                errors.append(
                    f"File is empty: "
                    f"{file_path}"
                )

                continue

        if path.suffix.lower() != ".py":

            passed += 1
            continue

        validation = validate_python_file(
            path
        )

        if not validation["valid"]:

            failed += 1

            errors.append(
                f"Python syntax error in "
                f"{file_path}: "
                f"{validation['error']}"
            )

            continue

        source = validation["source"]

        python_files.append(
            (
                file_path,
                path,
                source
            )
        )

        if is_test_file(path):

            test_files.append(
                (
                    file_path,
                    path
                )
            )

    # ----------------------------------------------
    # Detect unsupported pytest usage
    # ----------------------------------------------

    for file_path, path, source in python_files:

        imports = find_external_imports(
            source
        )

        if (
            is_test_file(path)
            and "pytest" in imports
        ):

            failed += 1

            error = (
                f"Test file {file_path} "
                f"requires pytest, but the project "
                f"does not declare pytest as a dependency. "
                f"Use Python unittest instead."
            )

            errors.append(error)

    # ----------------------------------------------
    # Run unittest suite
    # ----------------------------------------------

    if test_files:

        pytest_dependency_error = any(
            "requires pytest" in error
            for error in errors
        )

        if not pytest_dependency_error:

            print(
                "\n🧪 Running unit-test suite..."
            )

            suite_result = run_test_suite(
                project_dir
            )

            execution_results.append({
                "type": "test_suite",
                "file": "tests",
                **suite_result
            })

            if suite_result["passed"]:

                print(
                    "✅ Unit tests passed."
                )

                passed += len(test_files)

            else:

                print(
                    "❌ Unit tests failed."
                )

                failed += len(test_files)

                error_message = (
                    suite_result["stderr"].strip()
                    or suite_result["stdout"].strip()
                    or "Unit tests failed."
                )

                errors.append(
                    f"Test suite failed: "
                    f"{error_message}"
                )

    # ----------------------------------------------
    # Run non-test Python files
    # ----------------------------------------------

    for file_path, path, source in python_files:

        if is_test_file(path):
            continue

        # Interactive CLI programs should not be
        # executed automatically.
        if (
            "input(" in source
            or "input (" in source
        ):

            print(
                f"⏭️ Skipping interactive CLI: "
                f"{file_path}"
            )

            execution_results.append({
                "type": "interactive_cli",
                "file": file_path,
                "return_code": None,
                "stdout": "",
                "stderr": "",
                "passed": True
            })

            passed += 1
            continue

        result = run_python_file(
            path,
            project_dir
        )

        execution_results.append({
            "type": "python_module",
            "file": file_path,
            **result
        })

        if result["passed"]:

            passed += 1

        else:

            failed += 1

            error_message = (
                result["stderr"].strip()
                or result["stdout"].strip()
                or "Execution failed."
            )

            errors.append(
                f"Execution failed in "
                f"{file_path}: "
                f"{error_message}"
            )

    # ----------------------------------------------
    # Final result
    # ----------------------------------------------

    total_files = len(
        generated_files
    )

    status = (
        "passed"
        if failed == 0
        else "failed"
    )

    test_results = {
        "status": status,
        "total_files": total_files,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "execution_results": execution_results
    }

    print(
        "\n========== TESTER OUTPUT =========="
    )

    print(
        f"Status: {status}"
    )

    print(
        f"Files: {total_files}"
    )

    print(
        f"Passed: {passed}"
    )

    print(
        f"Failed: {failed}"
    )

    if errors:

        print("\nErrors:")

        for error in errors:

            print(
                f"  ❌ {error}"
            )

    print(
        "===================================\n"
    )

    return {
        **state,
        "generated_files": generated_files,
        "test_results": test_results,
        "errors": errors
    }