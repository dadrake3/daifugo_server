# =============
# --- Setup ---
# -------------

# Create the AppSync GraphQL api.
resource "aws_appsync_graphql_api" "appsync" {
  name                = "${var.prefix}_appsync"
  schema              = file("schema.graphql")
  authentication_type = "API_KEY"
}

# Create the API key.
resource "aws_appsync_api_key" "appsync_api_key" {
  api_id = aws_appsync_graphql_api.appsync.id
}

# ===================
# --- Datasources ---
# -------------------

# Dyanmodb Datasources

resource "aws_appsync_datasource" "game_table_datasource" {
  api_id           = aws_appsync_graphql_api.appsync.id
  name             = "${var.prefix}_game_table_datasource"
  service_role_arn = aws_iam_role.appsync_role.arn
  type             = "AMAZON_DYNAMODB"

  dynamodb_config {
    table_name = aws_dynamodb_table.game_table.name
  }
}

resource "aws_appsync_datasource" "player_table_datasource" {
  api_id           = aws_appsync_graphql_api.appsync.id
  name             = "${var.prefix}_player_table_datasource"
  service_role_arn = aws_iam_role.appsync_role.arn
  type             = "AMAZON_DYNAMODB"

  dynamodb_config {
    table_name = aws_dynamodb_table.player_table.name
  }
}

resource "aws_appsync_datasource" "hand_table_datasource" {
  api_id           = aws_appsync_graphql_api.appsync.id
  name             = "${var.prefix}_hand_table_datasource"
  service_role_arn = aws_iam_role.appsync_role.arn
  type             = "AMAZON_DYNAMODB"

  dynamodb_config {
    table_name = aws_dynamodb_table.hand_table.name
  }
}

resource "aws_appsync_datasource" "state_table_datasource" {
  api_id           = aws_appsync_graphql_api.appsync.id
  name             = "${var.prefix}_state_table_datasource"
  service_role_arn = aws_iam_role.appsync_role.arn
  type             = "AMAZON_DYNAMODB"

  dynamodb_config {
    table_name = aws_dynamodb_table.state_table.name
  }
}

# Lambda Datasources

# Create data source in appsync from lambda function.
resource "aws_appsync_datasource" "join_game_datasource" {
  name             = "${var.prefix}_join_game_datasource"
  api_id           = aws_appsync_graphql_api.appsync.id
  service_role_arn = aws_iam_role.appsync_role.arn
  type             = "AWS_LAMBDA"
  lambda_config {
    function_arn = aws_lambda_function.join_game_lambda.arn
  }
}


# =================
# --- Resolvers ---
# -----------------

# Unit VTL Resolvers

resource "aws_appsync_resolver" "create_game_resolver" {
  api_id      = aws_appsync_graphql_api.appsync.id
  type        = "Mutation"
  field       = "createGame"
  data_source = aws_appsync_datasource.game_table_datasource.name

  request_template  = file("./resolvers/create_game.vtl")
  response_template = file("./resolvers/response.vtl")
}
resource "aws_appsync_resolver" "update_game_resolver" {
  api_id      = aws_appsync_graphql_api.appsync.id
  type        = "Mutation"
  field       = "updateGame"
  data_source = aws_appsync_datasource.game_table_datasource.name

  request_template  = file("./resolvers/update_game.vtl")
  response_template = file("./resolvers/response.vtl")
}

resource "aws_appsync_resolver" "create_player_resolver" {
  api_id      = aws_appsync_graphql_api.appsync.id
  type        = "Mutation"
  field       = "createPlayer"
  data_source = aws_appsync_datasource.player_table_datasource.name

  request_template  = file("./resolvers/create_player.vtl")
  response_template = file("./resolvers/response.vtl")
}

resource "aws_appsync_resolver" "update_player_resolver" {
  api_id      = aws_appsync_graphql_api.appsync.id
  type        = "Mutation"
  field       = "updatePlayer"
  data_source = aws_appsync_datasource.player_table_datasource.name

  request_template  = file("./resolvers/update_player.vtl")
  response_template = file("./resolvers/response.vtl")
}

resource "aws_appsync_resolver" "create_hand_resolver" {
  api_id      = aws_appsync_graphql_api.appsync.id
  type        = "Mutation"
  field       = "createHand"
  data_source = aws_appsync_datasource.hand_table_datasource.name

  request_template  = file("./resolvers/create_hand.vtl")
  response_template = file("./resolvers/response.vtl")
}

resource "aws_appsync_resolver" "update_hand_resolver" {
  api_id      = aws_appsync_graphql_api.appsync.id
  type        = "Mutation"
  field       = "updateHand"
  data_source = aws_appsync_datasource.hand_table_datasource.name

  request_template  = file("./resolvers/update_hand.vtl")
  response_template = file("./resolvers/response.vtl")
}

resource "aws_appsync_resolver" "create_state_resolver" {
  api_id      = aws_appsync_graphql_api.appsync.id
  type        = "Mutation"
  field       = "createState"
  data_source = aws_appsync_datasource.state_table_datasource.name

  request_template  = file("./resolvers/create_state.vtl")
  response_template = file("./resolvers/response.vtl")
}

resource "aws_appsync_resolver" "update_state_resolver" {
  api_id      = aws_appsync_graphql_api.appsync.id
  type        = "Mutation"
  field       = "updateState"
  data_source = aws_appsync_datasource.state_table_datasource.name

  request_template  = file("./resolvers/update_state.vtl")
  response_template = file("./resolvers/response.vtl")
}

# Lambda Resolvers

# Create resolver using the velocity templates in /resolvers/lambda.
resource "aws_appsync_resolver" "listPeople_resolver" {
  api_id      = aws_appsync_graphql_api.appsync.id
  type        = "Mutation"
  field       = "joinGame"
  data_source = aws_appsync_datasource.join_game_datasource.name

  # request_template  = file("./resolvers/lambda/request.vtl")
  # response_template = file("./resolvers/lambda/response.vtl")
}