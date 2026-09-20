from pathlib import Path
import ast
import subprocess
import sys

from graph.state import ProjectState
from tools.filesystem import get_project_dir


def normalize_path(file_path: str) -> str:
    """
    Normalize generated file paths.

    Removes the generated_project/ prefix if present.
    """

    file_path = file_path.replace("\\", "/")

    if file_path.startswith("generated_project/"):
        file_path = file_path[len("generated_project/"):]

    return file_path


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
        source = path.read_text(
            encoding="utf-8"
        )

        ast.parse(source)

        return {
            "status": "passed",
            "file": str(path)
        }

    except SyntaxError as error:

        return {
            "status": "failed",
            "file": str(path),
            "error": (
                f"SyntaxError: {error.msg} "
                f"at line {error.lineno}"
            )
        }

    except Exception as error:

        return {
            "status": "failed",
            "file": str(path),
            "error": str(error)
        }


def find_external_imports(path: Path) -> list[str]:
    """
    Find non-standard/external imports.

    This is mainly used to detect unnecessary dependencies
    such as pytest when the project does not require them.
    """

    try:

        source = path.read_text(
            encoding="utf-8"
        )

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


def run_test_suite(project_dir: Path) -> dict:
    """
    Run unittest test discovery inside the project.
    """

    tests_dir = project_dir / "tests"

    if not tests_dir.exists():

        return {
            "status": "skipped",
            "passed": 0,
            "failed": 0,
            "error": "No tests directory found."
        }

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
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=20
        )

        if result.returncode == 0:

            return {
                "status": "passed",
                "passed": result.stdout.count("ok"),
                "failed": 0,
                "output": result.stdout.strip()
            }

        return {
            "status": "failed",
            "passed": result.stdout.count("ok"),
            "failed": 1,
            "error": (
                result.stderr.strip()
                or result.stdout.strip()
                or "Test suite failed."
            )
        }

    except subprocess.TimeoutExpired:

        return {
            "status": "failed",
            "passed": 0,
            "failed": 1,
            "error": "Test suite timed out."
        }

    except Exception as error:

        return {
            "status": "failed",
            "passed": 0,
            "failed": 1,
            "error": str(error)
        }


def run_python_file(
    path: Path,
    project_dir: Path
) -> dict:
    """
    Run a non-interactive Python file.
    """

    try:

        result = subprocess.run(
            [
                sys.executable,
                str(path)
            ],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:

            return {
                "status": "passed",
                "file": str(path),
                "output": result.stdout.strip()
            }

        return {
            "status": "failed",
            "file": str(path),
            "error": (
                result.stderr.strip()
                or result.stdout.strip()
                or "Python file execution failed."
            )
        }

    except subprocess.TimeoutExpired:

        return {
            "status": "skipped",
            "file": str(path),
            "error": "Execution timed out. File may be interactive."
        }

    except Exception as error:

        return {
            "status": "failed",
            "file": str(path),
            "error": str(error)
        }


def tester_agent(state: ProjectState):

    project_id = state.get("project_id")

    if not project_id:

        error = "Project ID is missing from project state."

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

    # Get the isolated project directory.
    project_dir = get_project_dir(project_id)

    generated_files = state.get(
        "generated_files",
        []
    )

    tasks = state.get(
        "tasks",
        []
    )

    # Collect files from generated_files and tasks.
    all_files = []

    for file_path in generated_files:

        if file_path:
            all_files.append(file_path)

    for task in tasks:

        file_path = task.get("path")

        if file_path:
            all_files.append(file_path)

    # Normalize and remove duplicates.
    unique_files = []

    seen = set()

    for file_path in all_files:

        normalized = normalize_path(
            str(file_path)
        )

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)

        unique_files.append(normalized)

    syntax_results = []
    execution_results = []
    errors = []

    python_files = []

    # Validate generated files.
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

    # Detect unnecessary pytest dependency.
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

    # Run unittest suite.
    test_suite_result = run_test_suite(
        project_dir
    )

    if test_suite_result["status"] == "failed":

        errors.append(
            test_suite_result.get(
                "error",
                "Test suite failed."
            )
        )

    # Run non-test Python files.
    for file_path in python_files:

        if is_test_file(file_path):
            continue

        path = project_dir / file_path

        # Skip obvious interactive CLI programs.
        try:

            source = path.read_text(
                encoding="utf-8"
            )

            interactive_markers = [
                "input(",
                "getpass(",
            ]

            if any(
                marker in source
                for marker in interactive_markers
            ):
                execution_results.append({
                    "status": "skipped",
                    "file": file_path,
                    "reason": "Interactive CLI program."
                })

                continue

        except Exception:
            pass

        result = run_python_file(
            path,
            project_dir
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

    syntax_failed = sum(
        1
        for result in syntax_results
        if result["status"] == "failed"
    )

    execution_failed = sum(
        1
        for result in execution_results
        if result["status"] == "failed"
    )

    if errors:

        overall_status = "failed"

    elif test_suite_result["status"] == "skipped":

        overall_status = "passed"

    else:

        overall_status = "passed"

    total_files = len(unique_files)

    passed_files = max(
        0,
        total_files
        - syntax_failed
        - execution_failed
    )

    return {
        **state,

        "test_results": {
            "status": overall_status,

            "project_id": project_id,

            "project_directory": str(
                project_dir
            ),

            "total_files": total_files,

            "passed": passed_files,

            "failed": (
                syntax_failed
                + execution_failed
            ),

            "errors": errors,

            "syntax_results": syntax_results,

            "execution_results": execution_results,

            "test_suite": test_suite_result,

            "pytest_detected": pytest_detected
        },

        "errors": errors
    }