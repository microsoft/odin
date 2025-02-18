from typing import List, TypedDict
from typing import Any, Dict, List

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        task: action chosen to answer question
        documents: list of documents
        chat_history: list of human inputs and AI outputs
    """

    question: str
    generation: str
    task: str
    documents: List[str]
    chat_history: List[Dict[str, Any]]
