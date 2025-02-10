from graph.state import GraphState
from chains.router import question_router, RouteQuery
from typing import Any, Dict

def route(state: GraphState) -> Dict[str, Any]:
    print("---ROUTE QUESTION---")
    actions = {
        'medical_records': 'a medical record database that contains specific claimant/patient information that can be used to answer specific questions about an individual',
        'conversate': 'If the user input mentions a summary at all or asks for general information about the claim or claimant, use this action. Also use if the user asks for a list of everything related to a specific topic'
    }
    actions_available = [k for k,v in actions.items()]
    action_descriptions = ''
    for action in actions_available:
        action_descriptions += f"\n'{action}': {actions[action]}"
    question = state["question"]
    chat_history = state['chat_history']
    graph_route: RouteQuery = question_router.invoke({"question": question, 'chat_history': chat_history, 'action_descriptions': action_descriptions})
    return {'task': graph_route.Action, 'documents': []}
