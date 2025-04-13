resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.scraper_lambda.function_name}"
  retention_in_days = 3
}
