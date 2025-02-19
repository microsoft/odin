# this is intended for fetching conversations from cosmos
# and offering a basic persistence methoddology as a stand
# in until we add support for
# https://python.langchain.com/v0.2/api_reference/_modules/langchain_community/chat_message_histories/cosmos_db.html#CosmosDBChatMessageHistory
import json
import os
import pickle
import sys
import uuid
from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient, ContainerProxy
from config import config
from models.conversation import Conversation
from azure.storage.blob import BlobServiceClient


class CosmosConversationService:
    def __init__(self):
        if config.cosmos_account_key is None or config.cosmos_account_key == "":
            if config.tenant_id is None or config.tenant_id == "":
                credentials = DefaultAzureCredential()
            else:
                credentials = DefaultAzureCredential(tenant_id=config.tenant_id)

            self.client = CosmosClient(config.cosmos_account_uri, credentials)
        else:
            self.client = CosmosClient(
                config.cosmos_account_uri, config.cosmos_account_key
            )

    def __try_and_get_container__(self) -> ContainerProxy:
        database_client = self.client.get_database_client(config.cosmos_db_name)
        container_client = database_client.get_container_client(
            config.cosmos_container_name
        )

        ### need this permission: Microsoft.DocumentDB/databaseAccounts/sqlDatabases/write
        ### in order to perform this try_get_create experience
        # try:
        #     database = self.client.create_database(config.cosmos_db_name)
        # except exceptions.CosmosResourceExistsError:
        #     database = self.get_database_client(config.cosmos_db_name)
        # try:
        #     container = database.create_container(
        #         id=config.cosmos_container_name,
        #         partition_key=PartitionKey(path=config.cosmos_partition_key),
        #     )
        # except exceptions.CosmosResourceExistsError:
        #     container = database.get_container_client(config.cosmos_container_name)
        # except exceptions.CosmosHttpResponseError:
        #     raise
        return container_client

    def get_conversations(self, user_id: str, claim_id: str) -> list[Conversation]:
        container = self.__try_and_get_container__()

        conversations_list = []

        for item in container.query_items(
            partition_key=claim_id,
            query=f"SELECT * FROM c WHERE c.user_id='{user_id}'",
        ):
            conversation = Conversation(
                claim_id=item["claim_id"],
                user_id=item["user_id"],
                user_group_id=item["user_group_id"],
                id=item["id"],
                messages=item["messages"],
            )
            conversations_list.append(conversation)

        return conversations_list

    def get_conversation(
        self, user_id: str, claim_id: str, conversation_id: int
    ) -> Conversation:
        container = self.__try_and_get_container__()

        for item in container.query_items(
            partition_key=claim_id,
            query=f'SELECT * FROM c WHERE c.id="{conversation_id}" and c.user_id="{user_id}"',
        ):
            return Conversation(
                claim_id=item["claim_id"],
                user_id=item["user_id"],
                user_group_id=item["user_group_id"],
                id=item["id"],
                messages=item["messages"],
            )

    def upsert_conversation(self, conversation: Conversation) -> Conversation:
        container = self.__try_and_get_container__()

        if conversation.id is None:
            conversation.id = str(uuid.uuid4())

        item = conversation.to_dict()

        container.upsert_item(body=item)

    def delete_conversation(self, user_id: str, claim_id, conversation_id):
        container = self.__try_and_get_container__()

        for item in container.query_items(
            partition_key=claim_id,
            query=f'SELECT * FROM c WHERE c.id="{conversation_id}" and c.user_id="{user_id}"',
        ):
            container.delete_item(item, partition_key=claim_id)


class PickleFileConversationService:
    def __init__(self):
        if (
            config.azure_storage_endpoint is not None
            and config.azure_storage_endpoint != ""
        ):
            if config.azure_storage_key is None or config.azure_storage_key == "":
                if config.tenant_id is None or config.tenant_id == "":
                    credentials = DefaultAzureCredential()
                else:
                    credentials = DefaultAzureCredential(tenant_id=config.tenant_id)
            else:
                credentials = config.azure_storage_key

            self.blob_service_client = BlobServiceClient(
                account_url=config.azure_storage_endpoint, credential=credentials
            )
        elif (
            config.azure_storage_connection_string is not None
            and config.azure_storage_connection_string != ""
        ):
            self.blob_service_client = BlobServiceClient.from_connection_string(
                conn_str=config.azure_storage_connection_string
            )
        else:
            directory_path = os.path.dirname(os.path.abspath(sys.argv[0]))
            self.filename = f"{directory_path}/conversation_store.pkl"
            self.blob_service_client = None

    def __get_file_state__(self) -> list[Conversation]:
        if self.blob_service_client is not None:
            container_client = self.blob_service_client.get_container_client(
                "conversation-store"
            )
            blob_client = container_client.get_blob_client("conversation-store.pkl")
            if blob_client.exists():
                blob_data = blob_client.download_blob().readall()
                data_list = pickle.loads(blob_data)
            else:
                data_list = []
            return [Conversation(**item) for item in data_list]

        if os.path.exists(self.filename):
            # Read existing data
            with open(self.filename, "rb") as file:
                try:
                    data_list = pickle.load(file)
                    if not isinstance(data_list, list):
                        return []
                    return [Conversation(**item) for item in data_list]
                except (pickle.PickleError, EOFError):
                    return []
        else:
            return []

    def __save_file_state__(self, conversations: list[Conversation]):
        if self.blob_service_client is not None:
            container_client = self.blob_service_client.get_container_client(
                "conversation-store"
            )
            blob_client = container_client.get_blob_client("conversation-store.pkl")
            data_list = [conversation.to_dict() for conversation in conversations]
            new_blob_data = pickle.dumps(data_list)
            blob_client.upload_blob(new_blob_data, overwrite=True)
            return

        data_list = [conversation.to_dict() for conversation in conversations]
        with open(self.filename, "wb") as file:
            pickle.dump(data_list, file)

    def get_conversations(self, user_id: str, claim_id: str) -> list[Conversation]:
        conversations = self.__get_file_state__()
        return [
            conversation
            for conversation in conversations
            if conversation.claim_id == claim_id and conversation.user_id == user_id
        ]

    def get_conversation(
        self, user_id: str, claim_id: str, conversation_id: int
    ) -> Conversation:
        conversations = self.__get_file_state__()
        for conversation in conversations:
            if (
                conversation.claim_id == claim_id
                and conversation.id == conversation_id
                and conversation.user_id == user_id
            ):
                return conversation

    def upsert_conversation(
        self, user_id: str, conversation: Conversation
    ) -> Conversation:
        conversations = self.__get_file_state__()
        for i, existing_conversation in (
            enumerate(conversations) if existing_conversation.user_id == user_id else []
        ):
            if (
                existing_conversation.claim_id == conversation.claim_id
                and existing_conversation.id == conversation.id
            ):
                conversations[i] = conversation
            self.__save_file_state__(conversations)
            return conversation

        conversations.append(conversation)
        self.__save_file_state__(conversations)
        return conversation

    def delete_conversation(self, user_id: str, claim_id, conversation_id):
        conversations = self.__get_file_state__()
        conversations = [
            conversation
            for conversation in conversations
            if conversation.claim_id != claim_id
            or conversation.id != conversation_id
            and conversation.user_id != user_id
        ]
        self.__save_file_state__(conversations)


if config.cosmos_account_uri is not None and config.cosmos_account_uri != "":
    conversation_service = CosmosConversationService()
else:
    conversation_service = PickleFileConversationService()

__all__ = [conversation_service]
