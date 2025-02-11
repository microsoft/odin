from typing import Any, Dict
from chains.conversation import conversation_chain
from graph.state import GraphState

def conversate(state: GraphState) -> Dict[str, Any]:
    print("---CONVERSATION--")
    question = state["question"]
    documents = state["documents"]
    chat_history = state['chat_history']

    generation = conversation_chain.invoke({"question": question, "chat_history": chat_history[-6:]})
    return {"documents": documents, "question": question, "generation": generation}