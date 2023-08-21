
data aws_caller_identity current {}

locals {
    account_id          = data.aws_caller_identity.current.account_id
    ecr_repository_name = "${var.prefix}-ecr"
    ecr_image_tag       = "latest"
}

resource "aws_ecr_repository" "repo" {
  name = local.ecr_repository_name
}

resource "null_resource" "lambda_image_builder" {
    triggers = {
        python_file = md5(file("${path.module}/lambda/app.py"))
        docker_file = md5(file("${path.module}/lambda/Dockerfile"))
    }

    provisioner "local-exec" {
        working_dir = "./lambda"
        command = <<EOF
                aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.${var.region}.amazonaws.com
                DOCKER_BUILDKIT=0 docker build -t ${aws_ecr_repository.repo.repository_url}:${local.ecr_image_tag} .
                docker push ${aws_ecr_repository.repo.repository_url}:${local.ecr_image_tag}
            EOF
    }
}

data "aws_ecr_image" "lambda_image" {
    depends_on = [null_resource.lambda_image_builder]
    repository_name = local.ecr_repository_name
    image_tag       = local.ecr_image_tag
}

resource "aws_lambda_function" "join_game_lambda" {
    depends_on = [null_resource.lambda_image_builder]
    function_name = "${var.prefix}_join_game"
    role = aws_iam_role.lambda_role.arn
    timeout = 300
    image_uri = "${aws_ecr_repository.repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
    package_type = "Image"

    architectures = ["arm64"] # need this because image built locally on arm64 m1 mac

    # handler = "app.join_game_handler"
    image_config {
        command = ["app.join_game_handler"]
    }


    environment {
        variables = {
            API_KEY = aws_appsync_api_key.appsync_api_key.key
            API_URL = aws_appsync_graphql_api.appsync.uris.GRAPHQL
        }
    }
}