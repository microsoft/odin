from langchain_openai import AzureChatOpenAI

llm_4o = AzureChatOpenAI(
    azure_deployment="DS-Claims-RnD-gpt-4o",
    api_version='2024-08-01-preview',
    temperature=0,
    model = 'gpt-4o'
)