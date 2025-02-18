# this is intended for fetching conversations from cosmos
# and offering a basic persistence methoddology as a stand
# in until we add support for
# https://python.langchain.com/v0.2/api_reference/_modules/langchain_community/chat_message_histories/cosmos_db.html#CosmosDBChatMessageHistory
import json
from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient, PartitionKey, ContainerProxy, exceptions
from config import config
from models.conversation import Conversation


class ConversationService:
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

    def try_and_get_container(self) -> ContainerProxy:
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

    def get_conversations(self, claim_id: str) -> list[Conversation]:
        container = self.try_and_get_container()

        conversations_list = []

        for item in container.query_items(
            partition_key=claim_id,
            query=f"SELECT * FROM c",
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

    def get_conversation(self, claim_id: str, conversation_id: int):
        container = self.try_and_get_container()

        for item in container.query_items(
            partition_key=claim_id,
            query=f'SELECT * FROM c WHERE c.id="{conversation_id}"',
        ):
            return Conversation(
                claim_id=item["claim_id"],
                user_id=item["user_id"],
                user_group_id=item["user_group_id"],
                id=item["id"],
                messages=item["messages"],
            )

    def upsert_conversation(
        self, conversation: Conversation
    ) -> Conversation:
        container = self.try_and_get_container()

        item = conversation.to_dict()

        container.upsert_item(body=item)

    def delete_conversation(self, claim_id, conversation_id):
        container = self.try_and_get_container()

        for item in container.query_items(
            partition_key=claim_id,
            query=f'SELECT * FROM c WHERE c.id="{conversation_id}"',
        ):
            container.delete_item(item, partition_key=claim_id)


conversation_service = ConversationService()

__all__ = [conversation_service]
