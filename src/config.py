import os
from dotenv import find_dotenv, load_dotenv

class AppConfig:
    def __init__(self):
        env_path = find_dotenv()
        load_dotenv(env_path, override=True)

        self.app_insights_instrumentation_key = os.getenv("AZURE_APP_INSIGHTS_INSTRUMENTATION_KEY")
        self.app_insights_connstr = os.getenv("AZURE_APP_INSIGHTS_CONN_STR")
        self.db_endpoint = os.getenv("AZURE_COSMOSDB_ENDPOINT")
        self.db_name = os.getenv("AZURE_COSMOSDB_DATABASE")
        self.db_container = os.getenv("AZURE_COSMOSDB_CONTAINER")
        self.db_chat_history_container = os.getenv("AZURE_COSMOSDB_CHATHISTORY_CONTAINER")
        self.db_key = os.getenv("AZURE_COSMOSDB_KEY")
        self.ai_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        self.ai_endpoint = os.getenv("AZURE_OPENAI_BASE_URL")
        self.ai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.ai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        