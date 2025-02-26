from typing import Any, Dict
from graph.state import GraphState
from langchain_community.retrievers import AzureAISearchRetriever
from config import config


def retrieve(state: GraphState) -> Dict[str, Any]:
    print("---RETRIEVE---")
    # get claimnumber
    claimnumber = state["claimnumber"]
    # Setup retriever

    retriever = AzureAISearchRetriever(
        service_name=config.azure_ai_search_service_name,
        index_name=config.azure_ai_search_index_name,
        api_key=config.azure_ai_search_api_key,
        content_key="content",
        top_k=10,
        filter=f"claimnumber eq '{claimnumber}'",
    )

    # retrieve document chunks
    question = state["question"]
    documents = retriever.invoke(question)

    return {"documents": documents}
