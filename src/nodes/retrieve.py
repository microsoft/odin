from typing import Any, Dict
import os
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from graph.state import GraphState
from langchain_community.retrievers import AzureAISearchRetriever
from claimnumber.claimnumber import claimnumber

def retrieve(state: GraphState) -> Dict[str, Any]:
    print("---RETRIEVE---")
    # Setup retriever
    retriever = AzureAISearchRetriever(content_key="chunk", top_k=10, index_name="sample-claims-docs", filter=f'ClaimNumberFilter eq {claimnumber}')
    # retrieve document chunks
    question = state["question"]
    documents = retriever.invoke(question)
 
    return {"documents": documents}