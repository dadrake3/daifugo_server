
data "aws_caller_identity" "current" {}

locals {
  account_id             = data.aws_caller_identity.current.account_id
  ecr_repository_name    = "${var.prefix}-ecr"
  ecr_image_tag          = "latest"
  join_game_lambda_name  = "${var.prefix}_join_game"
  start_game_lambda_name = "${var.prefix}_start_game"
  play_cards_lambda_name = "${var.prefix}_play_cards"
}

data "aws_ecr_repository" "repo" {
  name = local.ecr_repository_name
}


resource "null_resource" "lambda_image_builder" {
  triggers = {
    python_file = sha1(join("", [for f in fileset(path.module, "lambda/**") : filesha1(f)]))
    docker_file = sha1(file("${path.module}/lambda/Dockerfile"))
  }

  provisioner "local-exec" {
    working_dir = "./lambda"
    command     = <<EOF
                aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.${var.region}.amazonaws.com
                DOCKER_BUILDKIT=0 docker build -t ${data.aws_ecr_repository.repo.repository_url}:${local.ecr_image_tag} .
                docker push ${data.aws_ecr_repository.repo.repository_url}:${local.ecr_image_tag}
            EOF
  }
}

data "aws_ecr_image" "lambda_image" {
  depends_on      = [null_resource.lambda_image_builder]
  repository_name = local.ecr_repository_name
  image_tag       = local.ecr_image_tag
}

resource "aws_cloudwatch_log_group" "join_game_lambda_log_group" {
  name              = "/aws/lambda/${local.join_game_lambda_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_cloudwatch_log_group" "start_game_lambda_log_group" {
  name              = "/aws/lambda/${local.start_game_lambda_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_cloudwatch_log_group" "play_cards_lambda_log_group" {
  name              = "/aws/lambda/${local.play_cards_lambda_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_lambda_function" "join_game_lambda" {
  depends_on    = [null_resource.lambda_image_builder, aws_cloudwatch_log_group.join_game_lambda_log_group]
  function_name = local.join_game_lambda_name
  role          = aws_iam_role.lambda_role.arn
  timeout       = 300
  image_uri     = "${data.aws_ecr_repository.repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
  package_type  = "Image"

  architectures = ["arm64"] # need this because image built locally on arm64 m1 mac

  # handler = "app.join_game_handler"
  image_config {
    command = ["handlers.join_game_handler"]
  }

  environment {
    variables = {
      API_KEY = aws_appsync_api_key.appsync_api_key.key
      API_URL = aws_appsync_graphql_api.appsync.uris.GRAPHQL
    }
  }
}

resource "aws_lambda_function" "start_game_lambda" {
  depends_on    = [null_resource.lambda_image_builder, aws_cloudwatch_log_group.start_game_lambda_log_group]
  function_name = local.start_game_lambda_name
  role          = aws_iam_role.lambda_role.arn
  timeout       = 300
  image_uri     = "${data.aws_ecr_repository.repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
  package_type  = "Image"

  architectures = ["arm64"] # need this because image built locally on arm64 m1 mac

  image_config {
    command = ["handlers.start_game_handler"]
  }

  environment {
    variables = {
      API_KEY = aws_appsync_api_key.appsync_api_key.key
      API_URL = aws_appsync_graphql_api.appsync.uris.GRAPHQL
    }
  }
}

resource "aws_lambda_function" "play_cards_lambda" {
  depends_on    = [null_resource.lambda_image_builder, aws_cloudwatch_log_group.play_cards_lambda_log_group]
  function_name = local.play_cards_lambda_name
  role          = aws_iam_role.lambda_role.arn
  timeout       = 300
  image_uri     = "${data.aws_ecr_repository.repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
  package_type  = "Image"

  architectures = ["arm64"] # need this because image built locally on arm64 m1 mac

  image_config {
    command = ["handlers.play_cards_handler"]
  }

  environment {
    variables = {
      API_KEY = aws_appsync_api_key.appsync_api_key.key
      API_URL = aws_appsync_graphql_api.appsync.uris.GRAPHQL
    }
  }
}
