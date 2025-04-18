resource "aws_lambda_function" "scraper_lambda" {
  function_name = "scraper-lambda"
  runtime       = "nodejs22.x"
  handler       = "index.handler"
  role          = aws_iam_role.lambda_exec.arn

  filename         = "${path.module}/lambda/scraper/dist/index.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/scraper/dist/index.zip")

  timeout                        = 10
  memory_size                    = 128
#   reserved_concurrent_executions = 5
}

resource "aws_lambda_function" "gcs_lambda" {
  function_name = "gcs-lambda"
  runtime       = "python3.11"
  handler       = "main.lambda_handler"
  role          = aws_iam_role.lambda_exec.arn

  filename         = "${path.module}/lambda/gcs/dist/index.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/gcs/dist/index.zip")

  timeout                        = 10
  memory_size                    = 128
#   reserved_concurrent_executions = 5

  environment {
    variables = {
      GOOGLE_API_KEY = var.google_api_key
      GOOGLE_CX_ID   = var.google_cx_id
    }
  }
}
