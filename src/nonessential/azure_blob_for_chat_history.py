from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
import pickle
import sys
from config import config

def azure_blob_for_chat_history(request_json, conversation_id, recall_history_only=False, conv_result=None):

    # Azure Storage Account details
    AZURE_STORAGE_CONNECTION_STRING = config.azure_storage_connection_string
    CONTAINER_NAME = "chat-histories"
    BLOB_NAME = f"{conversation_id}.pkl"
    # define client
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blob_client = container_client.get_blob_client(BLOB_NAME)
    # if blob exists read history from file and append new data, 
    #   otherwise our new data is the beginning of our chat history
    if blob_client.exists():
        print("File exists. Reading content...")
        blob_data = blob_client.download_blob().readall().decode('utf-8')
        data_list = pickle.loads(blob_data)
    else:
        print("File does not exist. Creating a new one...")
        data_list = []
    if recall_history_only:
        return data_list
    else:
        new_data = [{
            'content': conv_result["question"],
            'date': request_json['messages'][0].get('date'),
            'role':'user'
        },{
            'content': conv_result["generation"],
            'date': request_json['messages'][0].get('date'),
            'role':'ai'
        }] # The item to append
        # Append new data
        data_list += new_data
        # write out chat history
        # Convert back to JSON and overwrite the blob
        new_blob_data = pickle.dumps(data_list)
        blob_client.upload_blob(new_blob_data, overwrite=True)
        print("File updated successfully.")