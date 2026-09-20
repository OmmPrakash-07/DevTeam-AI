from pathlib import Path
import ast

from graph.state import ProjectState


def tester_agent(state: ProjectState) -> ProjectState:

    generated_files = state.get("generated_files", [])

    if not generated_files:
        return {
            **state,
            "test_results": {
                "status": "failed",
                "total_files": 0,
                "passed": 0,
                "failed": 1,
                "errors": [
                    "No generated files were found."
                ]
            }
        }

    passed = 0
    failed = 0
    errors = []

    for file_path in generated_files:

        path = (
            Path(__file__).resolve().parents[2]
            / "generated_projects"
            / file_path
        )

        # Check file existence
        if not path.exists():

            failed += 1

            errors.append(
                f"File does not exist: {file_path}"
            )

            continue

        # Check empty files
        if path.stat().st_size == 0:

            failed += 1

            errors.append(
                f"File is empty: {file_path}"
            )

            continue

        # Python syntax check
        if path.suffix == ".py":

            try:

                source = path.read_text(
                    encoding="utf-8"
                )

                ast.parse(source)

            except SyntaxError as error:

                failed += 1

                errors.append(
                    f"Python syntax error in "
                    f"{file_path}: {error}"
                )

                continue

        passed += 1

    total_files = len(generated_files)

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
        "errors": errors
    }

    print("\n========== TESTER OUTPUT ==========")
    print(test_results)
    print("===================================\n")

    return {
        **state,
        "test_results": test_results,
        "errors": errors
    }