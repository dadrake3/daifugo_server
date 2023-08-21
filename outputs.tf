output "appsync_api_endpoint" {
  value = aws_appsync_graphql_api.appsync.uris
}
output "appsync_api_key" {
  value     = aws_appsync_api_key.appsync_api_key.key
  sensitive = true
}