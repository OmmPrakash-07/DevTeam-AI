from typing import TypedDict, List, Dict, Any


class ProjectState(TypedDict, total=False):
    user_request: str

    requirements: List[str]

    architecture: Dict[str, Any]

    tasks: List[Dict[str, Any]]

    generated_files: List[str]

    test_results: Dict[str, Any]

    errors: List[str]

    review: Dict[str, Any]

    final_response: str