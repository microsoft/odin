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

// user-assigned identity: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/managed-identity/user-assigned-identity
// module userAssignedIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
//   scope: resourceGroup(rg.name)
//   name: 'userAssignedIdentityDeployment'
//   params: {
//     // Required parameters
//     name: '${abbrs.managedIdentityUserAssignedIdentities}${resourceToken}'
//     // Non-required parameters
//     location: location
//   }
// }

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
      disableLocalAuth: true // todo: remove before OSS
      immediatePurgeDataOn30Days: true
    }
    roleAssignments: [
      {
        principalId: principalId
        roleDefinitionIdOrName: 'Log Analytics Contributor'
      }
      {
        principalId: principalId
        roleDefinitionIdOrName: 'Monitoring Contributor'
      }
    ]
    //// Consider creating stored queries and linked storage accounts; maybe we just include them as separate files?
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
    disableLocalAuth: true // todo: remove before OSS
    roleAssignments: [
      {
        principalId: principalId
        roleDefinitionIdOrName: 'Application Insights Component Contributor'
      }
      {
        principalId: principalId
        roleDefinitionIdOrName: 'Application Insights Snapshot Debugger'
      }
    ]
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
    roleAssignments: [
      {
        principalId: principalId
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
      {
        principalId: searchService.outputs.?systemAssignedMIPrincipalId!
        // principalId: userAssignedIdentity.outputs.principalId
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }

      // todo: add search service role assignment
      // todo: add app service role assignment (just in case they want to be able to display the full text)
    ]
    tags: tags
  }
}

// ai hub: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/cognitive-services/account
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
    roleAssignments: [
      {
        principalId: principalId
        roleDefinitionIdOrName: '64702f94-c441-49e6-a78b-ef80e0188fee' // Azure AI Developer
      }
      {
        principalId: searchService.outputs.?systemAssignedMIPrincipalId!
        // principalId: userAssignedIdentity.outputs.principalId
        roleDefinitionIdOrName: '64702f94-c441-49e6-a78b-ef80e0188fee' // Azure AI Developer
      }
      {
        principalId: principalId
        roleDefinitionIdOrName: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' // Cognitive Services OpenAI User
      }
      {
        principalId: searchService.outputs.?systemAssignedMIPrincipalId!
        // principalId: userAssignedIdentity.outputs.principalId
        roleDefinitionIdOrName: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' // Cognitive Services OpenAI User
      }
    ]
    tags: tags
  }
}

// ai hub: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/machine-learning-services/workspace
// module mlworkspace 'br/public:avm/res/machine-learning-services/workspace:0.10.0' = {
//   scope: resourceGroup(rg.name)
//   name: 'mlworkspace'
//   params: {
//     // Required parameters
//     name: '${abbrs.machineLearningServicesWorkspaces}${resourceToken}'
//     location: location
//     kind: 'Hub'
//     sku: 'Basic'
//     // Non-required parameters
//     associatedApplicationInsightsResourceId: component.outputs.resourceId
//     associatedKeyVaultResourceId: vault.outputs.resourceId
//     associatedStorageAccountResourceId: storageAccount.outputs.resourceId
//     connections: [
//       {
//         category: 'AIServices'
//         connectionProperties: {
//           authType: 'AAD'
//         }
//         metadata: {
//           ApiType: 'Azure'
//           ApiVersion: '2023-07-01-preview'
//           DeploymentApiVersion: '2023-10-01-preview'
//           Location: location
//           ResourceId: aiservices.outputs.resourceId
//         }
//         name: 'ai'
//         target: 'AzureOpenAI'
//       }
//     ]
//     managedIdentities: {
//       systemAssigned: true
//     }
//     publicNetworkAccess: 'Enabled'
//     // roleAssignments: [
//     //   {
//     //     principalId: principalId
//     //     roleDefinitionIdOrName: 'Azure AI Developer'
//     //   }
//     //   {
//     //     principalId: searchService.outputs.?systemAssignedMIPrincipalId!
//     //     roleDefinitionIdOrName: 'Azure AI Developer'
//     //   }
//     // ]
//     // workspaceHubConfig: {
//     //   defaultWorkspaceResourceGroup: resourceGroup(rg.name).reasourceId
//     // }
//   }
// }

// search: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/search/search-service
module searchService 'br/public:avm/res/search/search-service:0.9.0' = {
  scope: resourceGroup(rg.name)
  name: 'searchServiceDeployment'
  params: {
    name: '${abbrs.searchSearchServices}${resourceToken}'
    location: location
    disableLocalAuth: true // todo: remove before OSS
    managedIdentities: {
      // userAssignedResourceIds: [userAssignedIdentity.outputs.resourceId]
      systemAssigned: true
    }
    roleAssignments: [
      {
        principalId: principalId
        roleDefinitionIdOrName: 'Search Service Contributor'
      }
      {
        principalId: principalId
        roleDefinitionIdOrName: 'Search Index Data Contributor'
      }
      {
        // principalId: userAssignedIdentity.outputs.principalId
        principalId: site.outputs.?systemAssignedMIPrincipalId!
        roleDefinitionIdOrName: 'Search Index Data Contributor'
      }
    ]
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

/*
TODO: possible bug in AVM Bicep module... should investigate
*/

module dbRoleAssignments './db-assignments.bicep' = {
  scope: resourceGroup(rg.name)
  name: 'sqlRoleAssignmentDeployment'
  params: {
    databaseAccountName: databaseAccount.outputs.name
    principalIds: [principalId]
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
      // userAssignedResourceIds: [userAssignedIdentity.outputs.resourceId]
      systemAssigned: true
    }
    appSettingsKeyValuePairs: {
      ENABLE_ORYX_BUILD: 'True'
      SCM_DO_BUILD_DURING_DEPLOYMENT: 'True'
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

output AZURE_OPENAI_ENDPOINT string = aiservices.outputs.endpoint
output AZURE_OPENAI_DEPLOYMENT string = chatDeploymentName
output AZURE_OPENAI_VERSION string = chatDeploymentVersion

output AZURE_AI_SEARCH_SERVICE_NAME string = searchService.outputs.name
output AZURE_AI_SEARCH_INDEX_NAME string = indexName

output COSMOS_ACCOUNT_URI string = databaseAccount.outputs.endpoint
output COSMOS_DB_NAME string = cosmosDbName
output COSMOS_CONTAINER_NAME string = cosmosContainerName
output COSMOS_PARTITION_KEY string = cosmosPartitionKey

output IS_DEPLOYED bool = false
output LANGCHAIN_TRACING_V2 bool = false

