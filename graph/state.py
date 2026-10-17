from typing import TypedDict

class AgentState(TypedDict,total=False):
    #User Request
    task: str
    repo_path: str
    #Orchestrator Agent
    next_agent: str
    orchestrator_reason: str
    #Analyst Agent
    analysis: str
    implementation_path: str
    #Developer Agent
    developer_summary: str
    changed_files:list[str]
    # QA Agent
    test_output: str
    tests_passed: bool
    review: str
    review_passed: str
    #Workflow
    iteration:int
    final_status:str

