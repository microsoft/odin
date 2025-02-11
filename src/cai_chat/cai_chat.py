from graph.graph import app
from typing import List, Any, Dict

def run_agent(query: str, chat_history: List[Dict[str, Any]] = []):
    result = app.invoke(
        {'question': query,
         'chat_history': chat_history,
         'documents': None}
        )
    
    return result