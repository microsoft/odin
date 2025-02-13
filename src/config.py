import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        
        load_dotenv()

        self.tenant_id = os.getenv("TENANT_ID")

        self.app_insights_connstr = os.getenv("APPINSIGHTS_CONNECTION_STRING")

        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.azure_openai_model = os.getenv("AZURE_OPENAI_MODEL")
        self.azure_openai_version = os.getenv("AZURE_OPENAI_VERSION")
        
        self.azure_ai_search_service_name = os.getenv("AZURE_AI_SEARCH_SERVICE_NAME")
        self.azure_ai_search_index_name = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")
        self.azure_ai_search_api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
        
        self.langchain_tracing_v2 = os.getenv("LANGCHAIN_TRACING_V2")
        self.is_deployed = os.getenv("IS_DEPLOYED")

config = Config()

__all__ = [config]
