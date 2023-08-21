# =============
# --- Roles ---
# -------------

# Lambda role

data "aws_iam_policy_document" "iam_lambda_role_document" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "${var.prefix}_iam_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.iam_lambda_role_document.json
}


# Appsync role

data "aws_iam_policy_document" "iam_appsync_role_document" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["appsync.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "appsync_role" {
  name               = "${var.prefix}_iam_appsync_role"
  assume_role_policy = data.aws_iam_policy_document.iam_appsync_role_document.json
}


# ================
# --- Policies ---
# ----------------

# Invoke Lambda policy

data "aws_iam_policy_document" "iam_invoke_lambda_policy_document" {
  statement {
    actions   = ["lambda:InvokeFunction"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "appsync_invoke_lambda" {
  name   = "${var.prefix}_iam_invoke_lambda_policy"
  policy = data.aws_iam_policy_document.iam_invoke_lambda_policy_document.json
}

# RW Dynamodb tables

data "aws_iam_policy_document" "dyanmodb_rw_policy_document" {
  statement {
    actions = ["dynamodb:*"]
    resources = [
      aws_dynamodb_table.player_table.arn,
      aws_dynamodb_table.game_table.arn,
      aws_dynamodb_table.state_table.arn,
      aws_dynamodb_table.hand_table.arn,
    ]
  }
}

resource "aws_iam_policy" "dynamodb_lambda_policy" {
  name        = "${var.prefix}_dynamodb_lambda_rw_policy"
  description = "This policy will be used by the lambda to write/get data from DynamoDB"
  policy      = data.aws_iam_policy_document.dyanmodb_rw_policy_document.json
}


# ===================
# --- Attachments ---
# -------------------

# Attach Invoke Lambda policy to AppSync role.

resource "aws_iam_role_policy_attachment" "appsync_invoke_lambda" {
  role       = aws_iam_role.appsync_role.name
  policy_arn = aws_iam_policy.appsync_invoke_lambda.arn
}

resource "aws_iam_role_policy_attachment" "lambda_rw_dynamodb" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.dynamodb_lambda_policy.arn
}

resource "aws_iam_role_policy_attachment" "appsync_rw_dynamodb" {
  role       = aws_iam_role.appsync_role.name
  policy_arn = aws_iam_policy.dynamodb_lambda_policy.arn
}