param userPrincipalId string
param apiPrincipalId string
param searchPrincipalId string
param databaseAccountName string

// represents roles that are recommended for the user but not required for either the api or search service
var developerRoles = [
  // Application Insights Data Contributor
  '641177b8-a67a-45b9-a033-47bc880bb21e'
  // Search Service Contributor
  '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
  // Application Insights Snapshot Debugger
  '08954f03-6346-4c2e-81c0-ec3a5cfae23b'
  // Application Insights Component Contributor
  'ae349356-3a1b-4a5e-921d-050484c6347e'
  // Monitoring Contributor
  '749f88d5-cbae-40b8-bcfc-e573ddc772fa'
  // Log Analytics Contributor
  '92aaf0da-9dab-42b6-94a3-d43ce8d16293'
]

// represents roles that are required for the user and api (but not the search service)
var appRoles = [
  // Search Index Data Contributor
  '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
]

// represents roles that are required for the user, api, and search service
var minimumRoles = [
  // Azure AI Developer
  '64702f94-c441-49e6-a78b-ef80e0188fee'
  // Cognitive Services OpenAI User
  '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
  // Storage Blob Data Contributor
  'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
]

resource developerRoleAssignments 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for role in developerRoles: {
    name: guid(subscription().id, resourceGroup().id, userPrincipalId, role)
    properties: {
      principalId: userPrincipalId
      principalType: 'User'
      roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', role)
    }
  }
]

resource userAppRolesAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for role in appRoles: {
    name: guid(subscription().id, resourceGroup().id, userPrincipalId, role)
    properties: {
      principalId: userPrincipalId
      principalType: 'User'
      roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', role)
    }
  }
]

resource apiAppRolesAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for role in appRoles: {
    name: guid(subscription().id, resourceGroup().id, apiPrincipalId, role)
    properties: {
      principalId: apiPrincipalId
      principalType: 'ServicePrincipal'
      roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', role)
    }
  }
]

resource userMinimalRolesAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for role in minimumRoles: {
    name: guid(subscription().id, resourceGroup().id, userPrincipalId, role)
    properties: {
      principalId: userPrincipalId
      principalType: 'User'
      roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', role)
    }
  }
]

resource apiMinimalRolesAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for role in minimumRoles: {
    name: guid(subscription().id, resourceGroup().id, apiPrincipalId, role)
    properties: {
      principalId: apiPrincipalId
      principalType: 'ServicePrincipal'
      roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', role)
    }
  }
]

resource searchMinimalRolesAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for role in minimumRoles: {
    name: guid(subscription().id, resourceGroup().id, searchPrincipalId, role)
    properties: {
      principalId: searchPrincipalId
      principalType: 'ServicePrincipal'
      roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', role)
    }
  }
]


// COSMOS DB ASSIGNMENTS
resource databaseAccount 'Microsoft.DocumentDB/databaseAccounts@2024-12-01-preview' existing = {
  name: databaseAccountName
}

// consider creating a custom role with ability to create databases and collections
resource userSqlRoleAssignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2021-04-15' = {
  parent: databaseAccount
  name: guid('cosmos-db-built-in-data-contributor-${uniqueString(userPrincipalId)}')
  properties: {
    roleDefinitionId: '${databaseAccount.id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002' // Cosmos DB Built-in Data Contributor
    principalId: userPrincipalId
    scope: databaseAccount.id
  }
}

resource apiSqlRoleAssignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2021-04-15' = {
  parent: databaseAccount
  name: guid('cosmos-db-built-in-data-contributor-${uniqueString(apiPrincipalId)}')
  properties: {
    roleDefinitionId: '${databaseAccount.id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002' // Cosmos DB Built-in Data Contributor
    principalId: apiPrincipalId
    scope: databaseAccount.id
  }
}
