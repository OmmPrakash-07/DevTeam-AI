from typing import TypedDict, List, Dict, Any, Literal, Optional


class ActivityEvent(TypedDict, total=False):
    agent_name: str
    display_name: str
    status: Literal["queued", "running", "completed", "failed"]
    message: str
    timestamp: str
    attempt_number: Optional[int]


class ProjectState(TypedDict, total=False):
    project_id: str

    user_request: str

    requirements: List[str]

    architecture: Dict[str, Any]

    tasks: List[Dict[str, Any]]

    generated_files: List[str]

    test_results: Dict[str, Any]

    errors: List[str]

    review: Dict[str, Any]

    final_response: str

    debug_attempts: int

    activity_history: List[ActivityEvent]

    current_active_agent: Optional[str]
