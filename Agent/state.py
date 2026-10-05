from typing import TypedDict, List, Dict, Any,Optional

class State(TypedDict):
    user_request: str
    sandbox: str
    plan: List[Dict[str, Any]]
    current_task: int
    execution_history: List[Dict[str, Any]]
    verification: Dict[str, Any]
    retry_count: int
    status: str
    error: Optional[str]
    final_response: str