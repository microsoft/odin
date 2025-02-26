from cai_chat.cai_chat import run_agent
from azure.ai.evaluation import RougeScoreEvaluator, RougeType, SimilarityEvaluator
from config import config
from langchain_openai import AzureOpenAIEmbeddings
from scipy import spatial

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

model_config = {
    "azure_endpoint": azure_endpoint,
    "api_key": azure_openai_api_key,
    "azure_deployment": "cai-gpt-4o",
}

question = "Has the claimant had any surgery"
truth = "The claimant has had a total knee replacement surgery"

# Get gpt-similarity score
answer1 = run_agent(query=question, claimnumber='1234', chat_history=[])['generation']
similarity_evaluator = SimilarityEvaluator(model_config=model_config)
result1 = similarity_evaluator(query=question, response=answer1, ground_truth=truth)
#answer2 = run_agent(query=question, claimnumber='4321', chat_history=[])['generation']
answer2 = 'Yes, the claimant has had a surgery'
result2 = similarity_evaluator(query=question, response=answer2, ground_truth=truth)

# get cosine similarity score:
cosine1 = 1 - spatial.distance.cosine(embeddings.embed_query(truth), embeddings.embed_query(answer1))
cosine2 = 1 - spatial.distance.cosine(embeddings.embed_query(truth), embeddings.embed_query(answer2))

print('Truth: ',truth)
print('Answer: ',answer1)
print('\n')
print('gpt-simimlarity: ',result1['similarity'])
print('cosine-similarity: ', cosine1 )

print('---------------------')
print('Truth: ',truth)
print('Answer: ',answer2)
print('\n')
print('gpt-simimlarity: ',result2['similarity'])
print('cosine-similarity: ', cosine2 )



   