targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Id of the user or app to assign application roles')
param principalId string = ''

param serviceName string = 'chat-app'

param azureOpenAIApiVersion string = '2024-08-01-preview'
param chatDeploymentName string = 'chat'
param chatDeploymentVersion string = '2024-08-06'
param embeddingDeploymentName string = 'embedding'

param indexName string = 'claims-index'

param cosmosDbName string = 'chathistory'
param cosmosContainerName string = 'messages'
param cosmosPartitionKey string = '/claim_id'

var tags = {
  'azd-env-name': environmentName
}

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

var cosmosAccountName = '${abbrs.documentDBDatabaseAccounts}${resourceToken}'

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// keyvault: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/key-vault/vault
module vault 'br/public:avm/res/key-vault/vault:0.11.3' = {
  scope: resourceGroup(rg.name)
  name: 'vaultDeployment'
  params: {
    name: '${abbrs.keyVaultVaults}${resourceToken}'
    location: location
    enablePurgeProtection: false
    tags: tags
  }
}

// log analytics: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/operational-insights/workspace
module workspace 'br/public:avm/res/operational-insights/workspace:0.11.0' = {
  scope: resourceGroup(rg.name)
  name: 'workspaceDeployment'
  params: {
    name: '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    location: location
    dataRetention: 30
    features: {
      immediatePurgeDataOn30Days: true
    }
    // linkedStorageAccounts: [
    //   {
    //     name: 'savedsearches-link'
    //     storageAccountIds: [
    //       storageAccount.outputs.resourceId
    //     ]
    //   }
    // ]
    // savedSearches: [
    //   {
    //     category: 'Security'
    //     displayName: 'Get a count of security events'
    //     name: 'getSecurityEventCount'
    //     query: 'SecurityEvent | summarize count() by EventID'
    //   }
    // ]
    tags: tags
  }
}

// app insights: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/insights/component
module component 'br/public:avm/res/insights/component:0.6.0' = {
  scope: resourceGroup(rg.name)
  name: 'componentDeployment'
  params: {
    name: '${abbrs.insightsComponents}${resourceToken}'
    location: location
    workspaceResourceId: workspace.outputs.resourceId
    retentionInDays: 30
    kind: 'web'
    tags: tags
  }
}

// storage account: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/storage/storage-account
module storageAccount 'br/public:avm/res/storage/storage-account:0.17.3' = {
  scope: resourceGroup(rg.name)
  name: 'storageAccountDeployment'
  params: {
    name: '${abbrs.storageStorageAccounts}${resourceToken}'
    location: location
    kind: 'BlobStorage'
    accessTier: 'Hot'
    skuName: 'Standard_LRS'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
    blobServices: {
      containers: [
        {
          name: 'docs'
          publicAccess: 'None'
        }
      ]
    }
    tags: tags
  }
}

// Azure Open AI: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/cognitive-services/account
// using this version of the resource vs AIServices allows AI Search index wizard to work
// might consider adding an AI Services resource as well to enable use of other cognitive services e.g. document intelligence or vision
module aiservices 'br/public:avm/res/cognitive-services/account:0.9.2' = {
  scope: resourceGroup(rg.name)
  name: 'aiHub'
  params: {
    name: '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: location
    kind: 'OpenAI'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
    customSubDomainName: resourceToken
    deployments: [
      {
        name: chatDeploymentName
        model: {
          format: 'OpenAI'
          name: 'gpt-4o'
          version: chatDeploymentVersion
        }
        sku: {
          capacity: 30
          name: 'Standard'
        }
      }
      {
        name: embeddingDeploymentName
        model: {
          format: 'OpenAI'
          name: 'text-embedding-ada-002'
          version: '2'
        }
        sku: {
          capacity: 30
          name: 'Standard'
        }
      }
    ]
    tags: tags
  }
}

// Azure ML Workspace https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/machine-learning-services/workspace
// this is required for preview tracing of langchain
module mlworkspace 'br/public:avm/res/machine-learning-services/workspace:0.10.0' = {
  scope: resourceGroup(rg.name)
  name: 'mlworkspace'
  params: {
    // Required parameters
    name: '${abbrs.machineLearningServicesWorkspaces}${resourceToken}'
    location: location
    kind: 'Hub'
    sku: 'Basic'
    // Non-required parameters
    associatedApplicationInsightsResourceId: component.outputs.resourceId
    associatedKeyVaultResourceId: vault.outputs.resourceId
    associatedStorageAccountResourceId: storageAccount.outputs.resourceId
    connections: [
      {
        category: 'AzureOpenAI'
        connectionProperties: {
          authType: 'AAD'
        }
        metadata: {
          ApiType: 'Azure'
          ApiVersion: '2023-07-01-preview'
          DeploymentApiVersion: azureOpenAIApiVersion
          Location: location
          ResourceId: aiservices.outputs.resourceId
        }
        name: 'ai'
        target: 'AzureOpenAI'
      }
    ]
    managedIdentities: {
      systemAssigned: true
    }
    publicNetworkAccess: 'Enabled'
  }
}

// search: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/search/search-service
module searchService 'br/public:avm/res/search/search-service:0.9.0' = {
  scope: resourceGroup(rg.name)
  name: 'searchServiceDeployment'
  params: {
    name: '${abbrs.searchSearchServices}${resourceToken}'
    location: location
    disableLocalAuth: true // todo: remove before OSS
    managedIdentities: {
      systemAssigned: true
    }
    tags: tags
  }
}

// cosmos: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/document-db/database-account
module databaseAccount 'br/public:avm/res/document-db/database-account:0.11.0' = {
  scope: resourceGroup(rg.name)
  name: 'databaseAccountDeployment'
  params: {
    name: cosmosAccountName
    location: location
    networkRestrictions: {
      ipRules: []
      networkAclBypass: 'AzureServices'
      publicNetworkAccess: 'Enabled'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    backupStorageRedundancy: 'Local'
    capabilitiesToAdd: ['EnableServerless']
    sqlDatabases: [
      {
        name: cosmosDbName
        containers: [
          {
            name: cosmosContainerName
            paths: [
              cosmosPartitionKey
            ]
          }
        ]
      }
    ]
    tags: tags
  }
}

// app service plan: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/web/serverfarm
module serverfarm 'br/public:avm/res/web/serverfarm:0.4.1' = {
  scope: resourceGroup(rg.name)
  name: 'serverfarmDeployment'
  params: {
    name: '${abbrs.webServerFarms}${resourceToken}'
    location: location
    tags: tags
    zoneRedundant: false
    kind: 'linux'
  }
}

// app service: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/web/site
module site 'br/public:avm/res/web/site:0.13.3' = {
  scope: resourceGroup(rg.name)
  name: 'siteDeployment'
  params: {
    name: '${abbrs.webSitesAppService}${resourceToken}'
    location: location
    kind: 'app'
    managedIdentities: {
      systemAssigned: true
    }
    appSettingsKeyValuePairs: {
      ENABLE_ORYX_BUILD: 'True'
      SCM_DO_BUILD_DURING_DEPLOYMENT: 'True'

      AZURE_APP_INSIGHTS_CONN_STR: component.outputs.connectionString
      AZURE_APP_INSIGHTS_INSTRUMENTATION_KEY: component.outputs.instrumentationKey

      AZURE_OPENAI_ENDPOINT: aiservices.outputs.endpoint
      AZURE_OPENAI_DEPLOYMENT: chatDeploymentName
      AZURE_OPENAI_VERSION: azureOpenAIApiVersion

      AZURE_AI_SEARCH_SERVICE_NAME: searchService.outputs.name
      AZURE_AI_SEARCH_INDEX_NAME: indexName

      COSMOS_ACCOUNT_URI: databaseAccount.outputs.endpoint
      COSMOS_DB_NAME: cosmosDbName
      COSMOS_CONTAINER_NAME: cosmosContainerName
      COSMOS_PARTITION_KEY: cosmosPartitionKey

      AZURE_STORAGE_ENDPOINT: storageAccount.outputs.primaryBlobEndpoint
    }
    serverFarmResourceId: serverfarm.outputs.resourceId
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      ftpsState: 'Disabled'
      scmDoBuildDuringDeployment: true
    }
    appInsightResourceId: component.outputs.resourceId
    logsConfiguration: {
      applicationLogs: {
        fileSystem: {
          level: 'Verbose'
        }
      }
      detailedErrorMessages: {
        enabled: true
      }
      failedRequestsTracing: {
        enabled: true
      }
      httpLogs: {
        fileSystem: {
          enabled: true
          retentionInDays: 1
          retentionInMb: 35
        }
      }
    }
    tags: union(tags, { 'azd-service-name': serviceName })
  }
}

module permissions 'permissions.bicep' = {
  scope: resourceGroup(rg.name)
  name: 'permissionsDeployment'
  params: {
    userPrincipalId: principalId
    apiPrincipalId: site.outputs.?systemAssignedMIPrincipalId!
    searchPrincipalId: searchService.outputs.?systemAssignedMIPrincipalId!
    databaseAccountName: databaseAccount.outputs.name
  }
}

output AZURE_APP_INSIGHTS_CONN_STR string = component.outputs.connectionString
output AZURE_APP_INSIGHTS_INSTRUMENTATION_KEY string = component.outputs.instrumentationKey

output AZURE_OPENAI_ENDPOINT string = aiservices.outputs.endpoint
output AZURE_OPENAI_DEPLOYMENT string = chatDeploymentName
output AZURE_OPENAI_VERSION string = azureOpenAIApiVersion

output AZURE_AI_SEARCH_SERVICE_NAME string = searchService.outputs.name
output AZURE_AI_SEARCH_INDEX_NAME string = indexName

output COSMOS_ACCOUNT_URI string = databaseAccount.outputs.endpoint
output COSMOS_DB_NAME string = cosmosDbName
output COSMOS_CONTAINER_NAME string = cosmosContainerName
output COSMOS_PARTITION_KEY string = cosmosPartitionKey

output AZURE_STORAGE_ENDPOINT string = storageAccount.outputs.primaryBlobEndpoint

output IS_DEPLOYED bool = false
output LANGCHAIN_TRACING_V2 bool = false
