#!/bin/bash

# Define the files to be uploaded
DATASOURCE_FILE="datasource.json"
INDEX_FILE="index.json"
SKILLSET_FILE="skillset.json"
INDEXER_FILE="indexer.json"

# Define the Azure Search service details
SEARCH_SERVICE_NAME="your-search-service-name"
SEARCH_API_KEY="your-search-api-key"

# Function to upload a definition
upload_definition() {
    local file=$1
    local endpoint=$2

    if [ -f "$file" ]; then
        curl -X PUT \
            -H "Content-Type: application/json" \
            -H "api-key: $SEARCH_API_KEY" \
            --data-binary "@$file" \
            "https://$SEARCH_SERVICE_NAME.search.windows.net/$endpoint?api-version=2020-06-30"
    else
        echo "File $file does not exist."
    fi
}

# Upload the datasource
# Add the connection string to the datasource file

# "connectionString": "ResourceId=/subscriptions/547d44d6-312f-4664-a069-86e2ec828c88/resourceGroups/rg-odin10/providers/Microsoft.Storage/storageAccounts/stwhk2scxvsxw5y;"
if [ -f "$DATASOURCE_FILE" ]; then
    jq '.credentials = {"connectionString": "ResourceId=/subscriptions/547d44d6-312f-4664-a069-86e2ec828c88/resourceGroups/rg-odin10/providers/Microsoft.Storage/storageAccounts/stwhk2scxvsxw5y;"}' "$DATASOURCE_FILE" > tmp.$$.json && mv tmp.$$.json "$DATASOURCE_FILE"
else
    echo "File $DATASOURCE_FILE does not exist."
fi
upload_definition $DATASOURCE_FILE "datasources/your-datasource-name"




# Upload the index
upload_definition $INDEX_FILE "indexes/your-index-name"

# Upload the skillset
upload_definition $SKILLSET_FILE "skillsets/your-skillset-name"

# Upload the indexer
upload_definition $INDEXER_FILE "indexers/your-indexer-name"

echo "Upload completed."