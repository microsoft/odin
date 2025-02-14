from typing import Any, Dict
from graph.state import GraphState
from langchain_community.retrievers import AzureAISearchRetriever
<<<<<<< HEAD
=======
from claimnumber.claimnumber import claimnumber
from config import config
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

>>>>>>> b983013549b19747cfa14874df06e647f071bd64

def retrieve(state: GraphState) -> Dict[str, Any]:
    print("---RETRIEVE---")
    # get claimnumber
    claimnumber = state['claimnumber']
    # Setup retriever

    if (
        config.azure_ai_search_api_key is None
        or config.azure_ai_search_service_name == ""
    ):
        if config.tenant_id is None or config.tenant_id == "":
            credentials = DefaultAzureCredential()
        else:
            credentials = DefaultAzureCredential(tenant_id=config.tenant_id)

        token_provider = get_bearer_token_provider(
            credentials, "https://cognitiveservices.azure.com/.default"
        )

        retriever = AzureAISearchRetriever(
            service_name=config.azure_ai_search_service_name,
            index_name=config.azure_ai_search_index_name,
            azure_ad_token_provider=token_provider,
            content_key="chunk",
            top_k=10,
            filter=f"ClaimNumberFilter eq {claimnumber}",
        )
    else:
        retriever = AzureAISearchRetriever(
            service_name=config.azure_ai_search_service_name,
            index_name=config.azure_ai_search_index_name,
            api_key=config.azure_ai_search_api_key,
            content_key="chunk",
            top_k=10,
            filter=f"ClaimNumberFilter eq {claimnumber}",
        )

    # retrieve document chunks
    question = state["question"]
    documents = retriever.invoke(question)

    return {"documents": documents}
