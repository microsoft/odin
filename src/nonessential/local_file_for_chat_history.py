import os
import pickle
import sys

def local_file_for_chat_history(request_json, conversation_id, recall_history_only=False, conv_result=None):
    directory_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    subdirectory = "chat_histories"
    file_name_only = f"{conversation_id}.pkl"
    filename = directory_path + '/' + subdirectory + '/' + file_name_only
    # if local file exists, read history from file and append new data; otherwise our new data is the beginning of our chat history
    # write out chat history
    if os.path.exists(filename):
        # Read existing data
        with open(filename, 'rb') as file:
            try:
                data_list = pickle.load(file)
                if not isinstance(data_list, list):
                    data_list = []
            except (pickle.PickleError, EOFError):
                data_list = []
    else:
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
        # Write back to file
        with open(filename, 'wb') as file:
            pickle.dump(data_list, file)
        return None