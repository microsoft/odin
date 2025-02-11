from typing import Any, Dict
from chains.generator import generation_chain
from graph.state import GraphState
from langchain_core.documents import Document


def generate(state: GraphState) -> Dict[str, Any]:
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    chat_history = state['chat_history']
    # inject retrieved documents and generate answer
    generation = generation_chain.invoke({"context": documents, "question": question, "chat_history": chat_history[-6:]})

    return {"generation": generation}