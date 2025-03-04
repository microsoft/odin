import os
from dotenv import load_dotenv

class Config:
    def __init__(self):

        load_dotenv()

        self.app_insights_instrumentation_key = os.getenv(
            "AZURE_APP_INSIGHTS_INSTRUMENTATION_KEY"
        )
        self.app_insights_connstr = os.getenv("AZURE_APP_INSIGHTS_CONN_STR")

        self.tenant_id = os.getenv("TENANT_ID")

        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.azure_openai_model = os.getenv("AZURE_OPENAI_MODEL")
        self.azure_openai_version = os.getenv("AZURE_OPENAI_VERSION")

        self.azure_ai_search_service_name = os.getenv("AZURE_AI_SEARCH_SERVICE_NAME")
        self.azure_ai_search_index_name = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")
        self.azure_ai_search_api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
        self.azure_ai_search_url = os.getenv("AZURE_AI_SEARCH_URL")
        
        self.langchain_tracing_v2 = os.getenv("LANGCHAIN_TRACING_V2")
        self.is_deployed = os.getenv("IS_DEPLOYED")

        self.cosmos_account_uri = os.getenv("COSMOS_ACCOUNT_URI")
        self.cosmos_account_key = os.getenv("COSMOS_ACCOUNT_KEY")
        self.cosmos_db_name = os.getenv("COSMOS_DB_NAME")
        self.cosmos_container_name = os.getenv("COSMOS_CONTAINER_NAME")
        self.cosmos_partition_key = os.getenv("COSMOS_PARTITION_KEY")

        self.azure_storage_connection_string = os.getenv(
            "AZURE_STORAGE_CONNECTION_STRING"
        )
        self.azure_storage_endpoint = os.getenv("AZURE_STORAGE_ENDPOINT")
        self.azure_storage_key = os.getenv("AZURE_STORAGE_KEY")

        config_vals = {
            "AZURE_APP_INSIGHTS_INSTRUMENTATION_KEY": self.app_insights_instrumentation_key,
            "AZURE_APP_INSIGHTS_CONN_STR": self.app_insights_connstr,
            "AZURE_TENANT_ID": self.tenant_id,
            "AZURE_OPENAI_ENDPOINT": self.azure_openai_endpoint,
            "AZURE_OPENAI_API_KEY": self.azure_openai_api_key,
            "AZURE_OPENAI_DEPLOYMENT": self.azure_openai_deployment,
            "AZURE_OPENAI_MODEL": self.azure_openai_model,
            "AZURE_OPENAI_VERSION": self.azure_openai_version,
            "AZURE_AI_SEARCH_SERVICE_NAME": self.azure_ai_search_service_name,
            "AZURE_AI_SEARCH_INDEX_NAME": self.azure_ai_search_index_name,
            "AZURE_AI_SEARCH_API_KEY": self.azure_ai_search_api_key,
            "COSMOS_ACCOUNT_URI": self.cosmos_account_uri,
            "COSMOS_ACCOUNT_KEY": self.cosmos_account_key,
            "COSMOS_DB_NAME": self.cosmos_db_name,
            "COSMOS_CONTAINER_NAME": self.cosmos_container_name,
            "COSMOS_PARTITION_KEY": self.cosmos_partition_key,
            "AZURE_STORAGE_CONNECTION_STRING": self.azure_storage_connection_string,
            "AZURE_STORAGE_ENDPOINT": self.azure_storage_endpoint,
            "AZURE_STORAGE_KEY": self.azure_storage_key,
        }

        for key, val in config_vals.items():
            if val:
                print(f"{key}: " + "*" * len(val))


config = Config()

__all__ = [config]
