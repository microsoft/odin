from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.retrievers import AzureAISearchRetriever
from src.config import config
from langchain_core.documents import Document
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
import asyncio
from azure.search.documents.indexes.models import (
    ScoringProfile,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    TextWeights,
)

# Config Variables
azure_endpoint: str = config.azure_openai_endpoint
azure_openai_api_key: str = config.azure_openai_api_key
azure_openai_api_version: str = config.azure_openai_version
azure_deployment: str = "text-embedding-ada-002"

vector_store_address: str = config.azure_ai_search_url
vector_store_password: str = config.azure_ai_search_api_key

# Instantiate Embedding Function
embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
    azure_deployment=azure_deployment,
    openai_api_version=azure_openai_api_version,
    azure_endpoint=azure_endpoint,
    api_key=azure_openai_api_key,
)

embedding_function = embeddings.embed_query

# Defin Index Fields
fields = [
    SimpleField(
        name="id",
        type=SearchFieldDataType.String,
        key=True
    ),
    SearchableField(
        name="content",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=len(embedding_function("Text")),
        vector_search_profile_name="myHnswProfile",
    ),
    SearchableField(
        name="source",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    # Additional field to store the title
    SearchableField(
        name="claimnumber",
        type=SearchFieldDataType.String,
        searchable=True,
        filterable=True
    ),
    # Additional field to store the title
    SearchableField(
        name="page",
        type=SearchFieldDataType.String,
        searchable=True
    ),
    SearchableField(
        name="metadata",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
]

# Create Index
index_name: str = "langchain-vectorstore"
vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=vector_store_address,
    azure_search_key=vector_store_password,
    index_name=index_name,
    embedding_function=embeddings.embed_query,
    fields=fields,
)

# Read Sample Data
doc_data = pd.read_csv("updated_sample_doc_text.csv", dtype={'ClaimNumber': str}, encoding='utf-8')
doc_name = "Sample-filled-in-MR.pdf"
# Build Doc Objects
sources = doc_data['DocumentName'].values.tolist()
pages = doc_data['Page'].values.tolist()
texts = doc_data['Text'].values.tolist()
claimnumbers = doc_data['ClaimNumber'].values.tolist()
documents = []
for source, page, text, claimnumber in zip(sources,pages,texts,claimnumbers):
    doc = Document(
        page_content=text,
        metadata={"source": source,
            "page": str(page),
            "claimnumber": str(claimnumber),
            "metadata": 'test'}
            )
    documents.append(doc)

# Chunk Docs
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=500, chunk_overlap=50
)
doc_splits = text_splitter.split_documents(documents)

# INgest Doc Chunks
doc_split_content = []
doc_split_metadata = []
for split in doc_splits:
    doc_split_content.append(split.page_content)
    doc_split_metadata.append(split.metadata)

vector_store.add_texts(
    doc_split_content,
    doc_split_metadata
)

# Test Retriever
# retriever = AzureAISearchRetriever(
#             service_name=config.azure_ai_search_service_name,
#             index_name="langchain-vectorstore",
#             api_key=config.azure_ai_search_api_key,
#             content_key="content",
#             top_k=5,
#             filter=f"claimnumber eq '1234'",
#         )
# print(retriever.invoke('surgery'))