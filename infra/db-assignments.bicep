param principalIds array = []
param databaseAccountName string

resource databaseAccount 'Microsoft.DocumentDB/databaseAccounts@2024-12-01-preview' existing = {
  name: databaseAccountName
}

resource sqlRoleAssignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2021-04-15' = [
  for principalId in principalIds: {
    parent: databaseAccount
    name: guid('cosmos-db-built-in-data-contributor-${uniqueString(principalId)}')
    properties: {
      roleDefinitionId: '${databaseAccount.id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002' // Cosmos DB Built-in Data Contributor
      principalId: principalId
      scope: databaseAccount.id
    }
  }
]
